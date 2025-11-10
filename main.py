from window import render

def main():
    try:
        render()
    except Exception as e:
        print("Erro fatal:", e)

if __name__ == "__main__":
    main()
