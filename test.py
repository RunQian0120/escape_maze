import multiprocessing

class LockedObject:
    def __init__(self, value):
        self.value = value
        # self.lock = multiprocessing.Lock()

    def update_value(self, new_value):
        # with self.lock:  # Ensure that only one process/thread can update at a time
        self.value = new_value

    def __repr__(self):
        return f"LockedObject(value={self.value})"

def update_object(shared_object, new_value):
    print(f"Updating object to {new_value}")
    shared_object.value.update_value(new_value)  # Safely modify the object

def main():
    # Create a manager
    with multiprocessing.Manager() as manager:
        # Create a shared object inside the manager with a lock
        shared_object = manager.Namespace()
        shared_object.value = LockedObject(5)

        print("Before update:", shared_object.value)
        
        # Create processes to modify the object concurrently
        process_1 = multiprocessing.Process(target=update_object, args=(shared_object, 10))
        process_2 = multiprocessing.Process(target=update_object, args=(shared_object, 20))
        
        process_1.start()
        process_2.start()
        
        process_1.join()
        process_2.join()

        print("After updates:", shared_object.value)

if __name__ == "__main__":
    main()
