from window import Window

def main():
    try:
        window = Window()
        window.render()
    except Exception as e:
        print("Erro fatal:", e)

if __name__ == "__main__":
    main()
