from services import *

def main():
    running = True
    printMenu()
    while running:
        running = handleMenuChoice("Wybierz opcję [1-8]: ")

if __name__ == "__main__":
    main()
