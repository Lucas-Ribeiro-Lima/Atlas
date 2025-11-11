from window import App


def main():
    try:
        app = App()
        app.render()
    except Exception as e:
        print(e)
        return -1
    return 0

if __name__ == "__main__":
    main()
