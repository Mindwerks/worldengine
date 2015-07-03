if __name__ == "__main__":
    from os import path, pardir
    import sys
    sys.path.append(path.join(path.dirname(path.realpath(__file__)), pardir))
    from cli import main
    main.main()
