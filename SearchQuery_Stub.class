import java.io.*;
import java.net.*;
public class Client {
// initialize socket and input output streams
private Socket socket = null;
private BufferedReader d = null;
private InputStream input = null;
private DataOutputStream out = null;
// constructor to put ip address and port
public Client(String address, int port)
{
// establish a connection
try {
socket = new Socket(address, port);
System.out.println("Connected");
System.out.println("Done with 1st program of DS");
// takes input from terminal
d = new BufferedReader(new InputStreamReader(System.in));
// sends output to the socket
out = new DataOutputStream(
socket.getOutputStream());
}
catch (UnknownHostException u) {
System.out.println(u);
return;
}
catch (IOException i) {
System.out.println(i);
return;
}
// string to read message from input
String line = "";
// keep reading until "Over" is input
while (!line.equals("Over")) {
try {
line = d.readLine();
out.writeUTF(line);
}
catch (IOException i) {
System.out.println(i);
}
}
// close the connection
try {
input.close();
out.close();
socket.close();
}
catch (IOException i) {
System.out.println(i);
}
}
public static void main(String args[])
{
Client client = new Client("127.0.0.1", 5000);
}
}
