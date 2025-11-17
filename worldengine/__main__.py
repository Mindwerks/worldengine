if __name__ == "__main__":
    import sys
    from os import pardir, path

    sys.path.append(path.join(path.dirname(path.realpath(__file__)), pardir))
    from cli import main

    main.main()
