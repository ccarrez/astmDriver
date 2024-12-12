import socket
from datetime import datetime

ENCODING = 'latin-1' # ou ascii...

STX = '\x02' # Message start token
ETX = '\x03' # Message end token
EXT5B = '\x035B'
EOT = '\x04' # ASTM session termination token
ENQ = '\x05' # ASTM session initialization token
ACK = '\x06' # Command accepted token
NAK = '\x15' # Command rejected token
ETB = '\x17' # Message chunk end token
ETB37 = '\x1737'
LF = '\x0A' # CR + LF shortcut
CR = '\x0D' # CR + LF shortcut
CRLF = CR + LF # CR + LF shortcut
RECORD_SEP = '\x0D' # \r # Message records delimiter
FIELD_SEP = '\x7C' # | # Record fields delimiter
REPEAT_SEP = '\x5C' # \ # Delimeter for repeated fields
COMPONENT_SEP = '\x5E' # ^ # Field components delimiter
ESCAPE_SEP = '\x26' # & # Date escape token

def cleanStr(data):
    output=""
    skip_next = False
    # Iterate through each character in the string
    for i in range(len(data)):
        if skip_next:
            # Skip this character and reset the flag
            skip_next = False
            continue
        if data[i] == STX:
            # Skip it and the next character
            skip_next = True
        else:
            # Otherwise, add the character to the result
            output += data[i]
    return output.replace(EXT5B,'').replace(ETB37,'').replace(ENQ,'').replace(ACK,'').replace(ETB,'').replace(ETX,'').replace(EOT,'').rstrip()

# in our case, the analyzer sends multiple messages in one transmission
# so we split the messages into separate files _{count}
# and re-use the initial header H|...
def export(content):
    current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"results_{current_datetime}.astm"
    headerRow=""
    count=0
    lines = content.splitlines()
    output=""
    for line in lines:
        line=line.strip()
        if line.startswith("H|"):
            headerRow=line
        if line.startswith("P|"):
            if(count>0):
                filename = f"results_{current_datetime}_{count}.astm"
                saveToFile(filename, output)
                output=headerRow+CR
            count+=1
        if "|" in line:
            output+=line+CR
    filename = f"results_{current_datetime}_{count}.astm"
    saveToFile(filename, output)
    
def saveToFile(filename, content):
    f = open(filename, "a") #append
    f.write(content)
    f.close()

def handle_astm_message(message):
    # return an ACK
    if(message != EOT):
        return ACK
    return EOT

def start_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}")

    while True:
        try:
            client_socket, addr = server_socket.accept()
            print(f"Connection from {addr}")
            handle_client(client_socket)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            client_socket.close()

def handle_client(client_socket):
    count = 0
    content = ""
    try:
        while True:
            data = client_socket.recv(1024).decode(ENCODING)
            if not data:
                break
            response = handle_astm_message(data)
            if response != EOT:
                    client_socket.send(response.encode(ENCODING))
                    content += cleanStr(data)
                    count += 1
            else:
                if count > 2:
                    export(content)
                content = ""
                count = 0
    except ConnectionResetError:
        print("Client disconnected abruptly")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()
        print("Client connection closed")

if __name__ == "__main__":
    start_server('localhost', 3121)
