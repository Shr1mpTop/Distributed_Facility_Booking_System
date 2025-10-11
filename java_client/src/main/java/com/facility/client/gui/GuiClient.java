package com.facility.client.gui;

import com.facility.client.common.ByteBufferWrapper;
import com.facility.client.common.MessageTypes;
import com.facility.client.common.NetworkClient;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;

public class GuiClient extends JFrame {
    private final NetworkClient network;
    private final JTextField dateField;
    private final JTextField timeField;
    private final JTextField durationField;
    private final JTextArea bookingArea;
    private final JComboBox<String> facilityList;

    public GuiClient(String serverIp, int serverPort) throws Exception {
        this.network = new NetworkClient(serverIp, serverPort);

        // Setup main window
        setTitle("Facility Booking System - Client");
        setSize(900, 700);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new BorderLayout(10, 10));

        // Top info panel
        JPanel topPanel = new JPanel();
        topPanel.add(new JLabel(String.format("Server: %s:%d", serverIp, serverPort)));
        add(topPanel, BorderLayout.NORTH);

        // Input panel
        JPanel inputPanel = new JPanel(new GridBagLayout());
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.insets = new Insets(5, 5, 5, 5);
        gbc.fill = GridBagConstraints.HORIZONTAL;

        // Date input
        gbc.gridx = 0; gbc.gridy = 0;
        inputPanel.add(new JLabel("Date (YYYY-MM-DD):"), gbc);
        gbc.gridx = 1;
        dateField = new JTextField(10);
        dateField.setText(new SimpleDateFormat("yyyy-MM-dd").format(new Date()));
        inputPanel.add(dateField, gbc);

        // Time input
        gbc.gridx = 0; gbc.gridy = 1;
        inputPanel.add(new JLabel("Start Time (HH:MM):"), gbc);
        gbc.gridx = 1;
        timeField = new JTextField(10);
        timeField.setText("09:00");
        inputPanel.add(timeField, gbc);

        // Duration input
        gbc.gridx = 0; gbc.gridy = 2;
        inputPanel.add(new JLabel("Duration (minutes):"), gbc);
        gbc.gridx = 1;
        durationField = new JTextField(10);
        durationField.setText("60");
        inputPanel.add(durationField, gbc);

        // Facility selection
        gbc.gridx = 0; gbc.gridy = 3;
        inputPanel.add(new JLabel("Facility:"), gbc);
        gbc.gridx = 1;
        facilityList = new JComboBox<>(new String[]{"Room A", "Room B", "Room C"});
        inputPanel.add(facilityList, gbc);

        add(inputPanel, BorderLayout.CENTER);

        // Button panel
        JPanel buttonPanel = new JPanel();
        JButton queryButton = new JButton("Query Availability");
        queryButton.addActionListener(this::onQueryClicked);
        buttonPanel.add(queryButton);

        JButton bookButton = new JButton("Book Facility");
        bookButton.addActionListener(this::onBookClicked);
        buttonPanel.add(bookButton);

        add(buttonPanel, BorderLayout.SOUTH);

        // Booking display area
        bookingArea = new JTextArea();
        bookingArea.setEditable(false);
        JScrollPane scrollPane = new JScrollPane(bookingArea);
        add(scrollPane, BorderLayout.EAST);
    }

    private void onQueryClicked(ActionEvent e) {
        try {
            ByteBufferWrapper request = new ByteBufferWrapper();
            request.writeUInt8(MessageTypes.MSG_QUERY_AVAILABILITY);
            request.writeString(dateField.getText());
            request.writeString(timeField.getText());
            request.writeString(durationField.getText());
            request.writeString((String) facilityList.getSelectedItem());

            ByteBufferWrapper response = network.sendRequest(request);
            int msgType = response.readUInt8();
            
            if (msgType == MessageTypes.MSG_RESPONSE_SUCCESS) {
                String result = response.readString();
                bookingArea.append(result + "\n");
            } else {
                String error = response.readString();
                JOptionPane.showMessageDialog(this,
                    error,
                    "Error",
                    JOptionPane.ERROR_MESSAGE);
            }
        } catch (IOException ex) {
            JOptionPane.showMessageDialog(this,
                "Network error: " + ex.getMessage(),
                "Error",
                JOptionPane.ERROR_MESSAGE);
        }
    }

    private void onBookClicked(ActionEvent e) {
        try {
            ByteBufferWrapper request = new ByteBufferWrapper();
            request.writeUInt8(MessageTypes.MSG_BOOK_FACILITY);
            request.writeString(dateField.getText());
            request.writeString(timeField.getText());
            request.writeString(durationField.getText());
            request.writeString((String) facilityList.getSelectedItem());

            ByteBufferWrapper response = network.sendRequest(request);
            int msgType = response.readUInt8();
            
            if (msgType == MessageTypes.MSG_RESPONSE_SUCCESS) {
                String result = response.readString();
                bookingArea.append("Booking successful: " + result + "\n");
            } else {
                String error = response.readString();
                JOptionPane.showMessageDialog(this,
                    error,
                    "Error",
                    JOptionPane.ERROR_MESSAGE);
            }
        } catch (IOException ex) {
            JOptionPane.showMessageDialog(this,
                "Network error: " + ex.getMessage(),
                "Error",
                JOptionPane.ERROR_MESSAGE);
        }
    }

    public static void main(String[] args) {
        if (args.length != 2) {
            System.out.println("Usage: java GuiClient <server_ip> <server_port>");
            System.exit(1);
        }

        SwingUtilities.invokeLater(() -> {
            try {
                GuiClient client = new GuiClient(args[0], Integer.parseInt(args[1]));
                client.setVisible(true);
            } catch (Exception e) {
                JOptionPane.showMessageDialog(null,
                    "Error starting client: " + e.getMessage(),
                    "Error",
                    JOptionPane.ERROR_MESSAGE);
                System.exit(1);
            }
        });
    }
}