# core/emotion_detector.py

import os
import io
import numpy as np
import torch
import torch.nn as nn
import librosa

from transformers import Wav2Vec2Model


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "fairhindiser",
    "checkpoints",
    "full_best.pt"
)

BASE_MODEL = "facebook/wav2vec2-base"

SAMPLE_RATE = 16000

EMOTIONS = [
    "angry",
    "happy",
    "neutral",
    "sad"
]

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ============================================================
# FAIRHINDISER HEAD
# ============================================================

class FairSERHead(nn.Module):
    """
    Classification head reconstructed from the
    FairHindiSER checkpoint.
    """

    def __init__(self):
        super().__init__()

        self.head = nn.Sequential(
            nn.Linear(768, 512),
            nn.LayerNorm(512),
            nn.ReLU(),
            nn.Dropout(0.2),

            nn.Linear(512, 256),
            nn.LayerNorm(256),
            nn.ReLU(),
            nn.Dropout(0.2),
        )

        self.classifier = nn.Linear(256, 4)

    def forward(self, x):
        x = self.head(x)
        return self.classifier(x)


# ============================================================
# LoRA LINEAR LAYER
# ============================================================

class LoRALinear(nn.Module):
    """
    Reconstructs the LoRA-modified projection used by
    the FairHindiSER checkpoint.

    Checkpoint matrix shapes:

        A = (in_features, rank)
        B = (rank, out_features)

    Therefore:

        x @ A @ B
    """

    def __init__(
        self,
        original_layer,
        A,
        B
    ):
        super().__init__()

        self.orig = original_layer

        self.A = nn.Parameter(
            A.clone().detach()
        )

        self.B = nn.Parameter(
            B.clone().detach()
        )

    def forward(self, x):

        original = self.orig(x)

        lora = torch.matmul(x, self.A)
        lora = torch.matmul(lora, self.B)

        return original + lora


# ============================================================
# FAIRHINDISER MODEL
# ============================================================

class FairSERModel(nn.Module):
    """
    FairHindiSER model reconstructed from the published
    full_best.pt checkpoint.

    Architecture:

        Wav2Vec2-base
             |
        mean pooling
             |
        768 -> 512
             |
        LayerNorm
             |
           ReLU
             |
        512 -> 256
             |
        LayerNorm
             |
           ReLU
             |
        256 -> 4
             |
        Emotion
    """

    def __init__(self):

        super().__init__()

        print("Initializing FairHindiSER")
        print(f"Device: {DEVICE}")

        # ----------------------------------------------------
        # Load Wav2Vec2 backbone
        # ----------------------------------------------------

        print("Loading Wav2Vec2 backbone...")

        self.backbone = Wav2Vec2Model.from_pretrained(
            BASE_MODEL
        )

        # ----------------------------------------------------
        # Classification head
        # ----------------------------------------------------

        self.head = FairSERHead()

        # ----------------------------------------------------
        # Load FairHindiSER checkpoint
        # ----------------------------------------------------

        print("Loading FairHindiSER checkpoint...")

        self._load_checkpoint()

        self.to(DEVICE)

        self.eval()

        print("FairHindiSER checkpoint loaded.")

    # ========================================================
    # CHECKPOINT LOADING
    # ========================================================

    def _load_checkpoint(self):

        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"FairHindiSER checkpoint not found:\n{MODEL_PATH}"
            )

        checkpoint = torch.load(
            MODEL_PATH,
            map_location="cpu",
            weights_only=True
        )

        if not isinstance(checkpoint, dict):
            raise RuntimeError(
                "Unexpected FairHindiSER checkpoint format."
            )

        # ----------------------------------------------------
        # Separate checkpoint sections
        # ----------------------------------------------------

        backbone_state = {}
        head_state = {}
        classifier_state = {}

        lora_state = {}

        for key, value in checkpoint.items():

            # Backbone parameters
            if key.startswith("backbone."):

                stripped_key = key[len("backbone."):]

                # LoRA parameters are handled separately
                if (
                    ".A" in stripped_key
                    or ".B" in stripped_key
                    or ".orig." in stripped_key
                ):
                    lora_state[stripped_key] = value

                else:
                    backbone_state[stripped_key] = value

            # Classification head
            elif key.startswith("head."):

                head_state[key] = value

            # Final classifier
            elif key.startswith("classifier."):

                classifier_state[key] = value

            # LoRA keys that may not fall into the above
            elif (
                ".A" in key
                or ".B" in key
                or ".orig." in key
            ):

                lora_state[key] = value

        # ----------------------------------------------------
        # Load normal Wav2Vec2 backbone parameters
        # ----------------------------------------------------

        if backbone_state:

            missing, unexpected = self.backbone.load_state_dict(
                backbone_state,
                strict=False
            )

            if missing:
                print(
                    f"Backbone missing parameters: {len(missing)}"
                )

            if unexpected:
                print(
                    f"Backbone unexpected parameters: "
                    f"{len(unexpected)}"
                )

        # ----------------------------------------------------
        # Load FairSER head
        # ----------------------------------------------------

        if head_state:

            self.head.head.load_state_dict(
                {
                    key[len("head."):]: value
                    for key, value in head_state.items()
                },
                strict=True
            )

        # ----------------------------------------------------
        # Load classifier
        # ----------------------------------------------------

        if classifier_state:

            self.head.classifier.load_state_dict(
                {
                    key[len("classifier."):]: value
                    for key, value in classifier_state.items()
                },
                strict=True
            )

        # ----------------------------------------------------
        # Load LoRA layers
        # ----------------------------------------------------

        self._load_lora(checkpoint)

    # ========================================================
    # LoRA RECONSTRUCTION
    # ========================================================

    def _load_lora(self, checkpoint):

        lora_layers = [8, 9, 10, 11]

        projection_names = [
            "q_proj",
            "v_proj"
        ]

        for layer_idx in lora_layers:

            layer = self.backbone.encoder.layers[layer_idx]

            for projection_name in projection_names:

                prefix = (
                    f"backbone.encoder.layers."
                    f"{layer_idx}.attention."
                    f"{projection_name}"
                )

                weight_key = f"{prefix}.orig.weight"
                bias_key = f"{prefix}.orig.bias"
                A_key = f"{prefix}.A"
                B_key = f"{prefix}.B"

                if (
                    weight_key not in checkpoint
                    or
                    A_key not in checkpoint
                    or
                    B_key not in checkpoint
                ):
                    continue

                original_weight = checkpoint[weight_key]
                original_bias = checkpoint.get(
                    bias_key,
                    None
                )

                A = checkpoint[A_key]
                B = checkpoint[B_key]

                # ------------------------------------------------
                # Verify expected shapes
                # ------------------------------------------------

                expected_in = original_weight.shape[1]
                expected_out = original_weight.shape[0]

                if A.shape[0] != expected_in:
                    raise RuntimeError(
                        f"Unexpected LoRA A shape for "
                        f"{prefix}: {A.shape}"
                    )

                if B.shape[1] != expected_out:
                    raise RuntimeError(
                        f"Unexpected LoRA B shape for "
                        f"{prefix}: {B.shape}"
                    )

                # ------------------------------------------------
                # Reconstruct original Linear layer
                # ------------------------------------------------

                original_linear = nn.Linear(
                    expected_in,
                    expected_out,
                    bias=original_bias is not None
                )

                original_linear.weight.data.copy_(
                    original_weight
                )

                if original_bias is not None:
                    original_linear.bias.data.copy_(
                        original_bias
                    )

                # ------------------------------------------------
                # Replace projection with LoRA layer
                # ------------------------------------------------

                lora_linear = LoRALinear(
                    original_linear,
                    A,
                    B
                )

                setattr(
                    layer.attention,
                    projection_name,
                    lora_linear
                )


# ============================================================
# SINGLE MODEL INSTANCE
# ============================================================

_MODEL = None


def get_model():
    """
    Load FairHindiSER only once.
    """

    global _MODEL

    if _MODEL is None:

        _MODEL = FairSERModel()

    return _MODEL


# ============================================================
# AUDIO PREPROCESSING
# ============================================================

def audio_data_to_numpy(audio_data):
    """
    Convert SpeechRecognition AudioData into:

        16 kHz
        mono
        float32

    waveform.

    IMPORTANT:
    Uses zero-mean / unit-variance normalization instead
    of peak normalization.

    This is the current FairHindiSER preprocessing test.
    """

    if audio_data is None:
        return None

    try:

        # ----------------------------------------------------
        # Convert SpeechRecognition audio to WAV
        # ----------------------------------------------------

        raw_data = audio_data.get_wav_data(
            convert_rate=SAMPLE_RATE,
            convert_width=2
        )

        # ----------------------------------------------------
        # Load audio
        # ----------------------------------------------------

        audio, _ = librosa.load(
            io.BytesIO(raw_data),
            sr=SAMPLE_RATE,
            mono=True
        )

        audio = audio.astype(
            np.float32
        )

        # ----------------------------------------------------
        # Validate
        # ----------------------------------------------------

        if len(audio) == 0:
            return None

        # ----------------------------------------------------
        # Zero-mean normalization
        # ----------------------------------------------------

        audio = audio - np.mean(audio)

        # ----------------------------------------------------
        # Unit-variance normalization
        # ----------------------------------------------------

        std = np.std(audio)

        if std > 1e-7:

            audio = audio / std

        return audio

    except Exception as e:

        print(
            f"Audio preprocessing error: {e}"
        )

        return None


# ============================================================
# EMOTION DETECTION
# ============================================================

@torch.no_grad()
def detect_emotion(audio_data):
    """
    Detect emotion from the user's voice.

    Returns:

        emotion
        confidence
    """

    # --------------------------------------------------------
    # Convert audio
    # --------------------------------------------------------

    audio = audio_data_to_numpy(
        audio_data
    )

    # --------------------------------------------------------
    # Missing/invalid audio
    # --------------------------------------------------------

    if audio is None:

        return "neutral", 0.0

    # --------------------------------------------------------
    # Ignore extremely short recordings
    # --------------------------------------------------------

    if len(audio) < SAMPLE_RATE * 0.25:

        return "neutral", 0.0

    # --------------------------------------------------------
    # Load model
    # --------------------------------------------------------

    model = get_model()

    # --------------------------------------------------------
    # Convert waveform to tensor
    # --------------------------------------------------------

    waveform = torch.tensor(
        audio,
        dtype=torch.float32
    ).unsqueeze(0).to(DEVICE)

    # --------------------------------------------------------
    # Attention mask
    #
    # Since this is a single unpadded recording, every
    # waveform sample is valid.
    # --------------------------------------------------------

    attention_mask = torch.ones(
        waveform.shape,
        dtype=torch.long,
        device=DEVICE
    )

    # --------------------------------------------------------
    # Wav2Vec2 backbone
    # --------------------------------------------------------

    outputs = model.backbone(
        input_values=waveform,
        attention_mask=attention_mask
    )

    # --------------------------------------------------------
    # Mean pooling
    # --------------------------------------------------------

    hidden_states = outputs.last_hidden_state

    pooled = hidden_states.mean(
        dim=1
    )

    # --------------------------------------------------------
    # FairSER head
    # --------------------------------------------------------

    features = model.head.head(
        pooled
    )

    logits = model.head.classifier(
        features
    )

    # --------------------------------------------------------
    # Probabilities
    # --------------------------------------------------------

    probabilities = torch.softmax(
        logits,
        dim=-1
    )

    confidence, index = torch.max(
        probabilities,
        dim=-1
    )

    emotion = EMOTIONS[
        index.item()
    ]

    confidence = confidence.item()

    return emotion, confidence


# ============================================================
# AUDIO ANALYSIS
# ============================================================

def analyze_voice(audio_data):
    """
    Return additional information about the recording.

    Useful for debugging/calibration.
    """

    audio = audio_data_to_numpy(
        audio_data
    )

    if audio is None:

        return {
            "emotion": "neutral",
            "confidence": 0.0,
            "duration": 0.0,
            "rms": 0.0
        }

    # --------------------------------------------------------
    # Duration
    # --------------------------------------------------------

    duration = len(audio) / SAMPLE_RATE

    # --------------------------------------------------------
    # RMS energy
    # --------------------------------------------------------

    rms = float(
        np.sqrt(
            np.mean(
                np.square(audio)
            )
        )
    )

    # --------------------------------------------------------
    # Emotion
    # --------------------------------------------------------

    emotion, confidence = detect_emotion(
        audio_data
    )

    return {
        "emotion": emotion,
        "confidence": confidence,
        "duration": duration,
        "rms": rms
    }