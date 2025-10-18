package com.facility.common;

import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketTimeoutException;

/**
 * Network Client
 * Handles UDP communication with server
 */
public class NetworkClient {
    private String serverIp;
    private int serverPort;
    private DatagramSocket socket;
    private int nextRequestId;
    private double dropRate;

    public NetworkClient(String serverIp, int serverPort) {
        this(serverIp, serverPort, 0.0);
    }

    public NetworkClient(String serverIp, int serverPort, double dropRate) {
        this.serverIp = serverIp;
        this.serverPort = serverPort;
        this.dropRate = dropRate;
        this.nextRequestId = 1;
        
        try {
            this.socket = new DatagramSocket();
            this.socket.setSoTimeout(MessageTypes.TIMEOUT_SECONDS * 1000);
        } catch (Exception e) {
            throw new RuntimeException("Failed to create socket: " + e.getMessage());
        }
    }

    public String getServerIp() {
        return serverIp;
    }

    public int getServerPort() {
        return serverPort;
    }

    public synchronized int getNextRequestId() {
        return nextRequestId++;
    }

    public byte[] sendRequest(byte[] requestData) {
        return sendRequest(requestData, MessageTypes.MAX_RETRIES, null);
    }

    public byte[] sendRequest(byte[] requestData, int retries, Integer timeout) {
        // Save original timeout
        int originalTimeout = 0;
        try {
            originalTimeout = socket.getSoTimeout();
            
            // Set custom timeout if provided
            if (timeout != null) {
                socket.setSoTimeout(timeout * 1000);
            }

            for (int attempt = 0; attempt < retries; attempt++) {
                try {
                    // Simulate packet drop on client side
                    if (Math.random() < dropRate) {
                        System.out.println("[DROP] Request dropped (attempt " + 
                            (attempt + 1) + "/" + retries + ")");
                        // Simulate timeout
                        Thread.sleep(MessageTypes.TIMEOUT_SECONDS * 1000);
                        continue;
                    }

                    // Send request
                    InetAddress address = InetAddress.getByName(serverIp);
                    DatagramPacket sendPacket = new DatagramPacket(
                        requestData, requestData.length, address, serverPort);
                    socket.send(sendPacket);

                    // Wait for response
                    byte[] receiveBuffer = new byte[MessageTypes.MAX_BUFFER_SIZE];
                    DatagramPacket receivePacket = new DatagramPacket(
                        receiveBuffer, receiveBuffer.length);
                    socket.receive(receivePacket);

                    // Extract actual data
                    byte[] responseData = new byte[receivePacket.getLength()];
                    System.arraycopy(receiveBuffer, 0, responseData, 0, receivePacket.getLength());
                    return responseData;

                } catch (SocketTimeoutException e) {
                    if (attempt < retries - 1) {
                        System.out.println("Timeout, retrying... (attempt " + 
                            (attempt + 2) + "/" + retries + ")");
                    } else {
                        System.out.println("Request timeout after all retries");
                        return null;
                    }
                }
            }
            return null;
            
        } catch (Exception e) {
            System.err.println("Error sending request: " + e.getMessage());
            return null;
        } finally {
            // Restore original timeout
            if (timeout != null) {
                try {
                    socket.setSoTimeout(originalTimeout);
                } catch (Exception e) {
                    // Ignore
                }
            }
        }
    }

    public void close() {
        if (socket != null && !socket.isClosed()) {
            socket.close();
        }
    }
}
