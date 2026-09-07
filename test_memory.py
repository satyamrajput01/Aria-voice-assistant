from core.memory import (
    save_memory,
    get_memory,
    get_all_memories,
    delete_memory
)

save_memory("personal", "name", "Satyam")
save_memory("preferences", "favorite_sport", "volleyball")

print("Name:")
print(get_memory("name"))

print("\nFavorite sport:")
print(get_memory("favorite_sport"))

print("\nAll memories:")
print(get_all_memories())

delete_memory("favorite_sport")

print("\nAfter deleting favorite sport:")
print(get_all_memories())