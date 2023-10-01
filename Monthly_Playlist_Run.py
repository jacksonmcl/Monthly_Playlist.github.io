import webbrowser

def main():
    host_url = "http://127.0.0.1:5000"

    if webbrowser.open(url=host_url, new=1):
        print("Success")
    else:
        print("Error")

if __name__ == "__main__":
    main()