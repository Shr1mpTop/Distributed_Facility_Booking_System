package com.facility.client.common;

import java.io.IOException;
import java.net.*;

public class NetworkClient {
    private final String serverIp;
    private final int serverPort;
    private final DatagramSocket socket;
    private int nextRequestId;

    public NetworkClient(String serverIp, int serverPort) throws SocketException {
        this.serverIp = serverIp;
        this.serverPort = serverPort;
        this.socket = new DatagramSocket();
        this.socket.setSoTimeout(MessageTypes.TIMEOUT_SECONDS * 1000);
        this.nextRequestId = 1;
    }

    public ByteBufferWrapper sendRequest(ByteBufferWrapper request) throws IOException {
        InetAddress serverAddress = InetAddress.getByName(serverIp);
        byte[] requestData = request.getData();
        DatagramPacket requestPacket = new DatagramPacket(
            requestData, requestData.length, serverAddress, serverPort);

        int retries = 0;
        while (retries < MessageTypes.MAX_RETRIES) {
            try {
                // Send request
                socket.send(requestPacket);

                // Prepare for response
                byte[] responseBuffer = new byte[MessageTypes.MAX_BUFFER_SIZE];
                DatagramPacket responsePacket = new DatagramPacket(
                    responseBuffer, responseBuffer.length);

                // Receive response
                socket.receive(responsePacket);

                // Create response buffer
                byte[] responseData = new byte[responsePacket.getLength()];
                System.arraycopy(responsePacket.getData(), 0, 
                               responseData, 0, responsePacket.getLength());
                return new ByteBufferWrapper(responseData);

            } catch (SocketTimeoutException e) {
                retries++;
                if (retries >= MessageTypes.MAX_RETRIES) {
                    throw new IOException("Request timed out after " + 
                                       MessageTypes.MAX_RETRIES + " retries");
                }
            }
        }

        throw new IOException("Failed to send request after " + 
                            MessageTypes.MAX_RETRIES + " retries");
    }

    public void close() {
        if (socket != null && !socket.isClosed()) {
            socket.close();
        }
    }
}