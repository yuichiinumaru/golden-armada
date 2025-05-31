import sys

def process_file(input_filepath):
    try:
        with open(input_filepath, 'r') as infile:
            content = infile.read()
    except FileNotFoundError:
        print(f"Error: File not found: {input_filepath}")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    chunk_size = 1000
    chunks = [content[i:i + chunk_size] for i in range(0, len(content), chunk_size)]

    for i, chunk in enumerate(chunks):
        try:
            with open(f'chunk_{i}.txt', 'w') as outfile:
                outfile.write(chunk)
        except Exception as e:
            print(f"Error writing to file chunk_{i}.txt: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <input_filepath>")
        sys.exit(1)

    input_filepath = sys.argv[1]
    process_file(input_filepath)
