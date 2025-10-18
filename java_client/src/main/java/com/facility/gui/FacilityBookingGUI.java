package com.facility.gui;

import com.facility.common.ByteBuffer;
import com.facility.common.MessageTypes;
import com.facility.common.NetworkClient;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import java.awt.*;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Calendar;

/**
 * Facility Booking System - GUI Client
 * GUI client using Swing
 */
public class FacilityBookingGUI extends JFrame {
    private NetworkClient network;
    
    // Query tab components
    private JComboBox<String> queryFacility;
    private JTextField queryDays;
    private JTextArea queryResult;
    
    // Book tab components
    private JComboBox<String> bookFacility;
    private JTextField bookDate;
    private JTextField bookTime;
    private JTextField bookDuration;
    private JTextArea bookResult;
    
    // Change tab components
    private JTextField changeId;
    private JTextField changeOffset;
    private JTextArea changeResult;
    
    // Operations tab components
    private JComboBox<String> lastTimeFacility;
    private JTextField extendId;
    private JTextField extendMinutes;
    private JTextArea opsResult;
    
    // Log area
    private JTextArea logText;
    
    // Tabs
    private JTabbedPane tabbedPane;
    
    // Color scheme
    private static final Color PRIMARY_COLOR = new Color(34, 34, 59);
    private static final Color SECONDARY_COLOR = new Color(74, 78, 105);
    private static final Color BACKGROUND_COLOR = new Color(247, 247, 250);
    private static final Color TEXT_COLOR = new Color(34, 34, 59);
    private static final Color ACCENT_COLOR = new Color(154, 140, 152);
    
    public FacilityBookingGUI(String serverIp, int serverPort) {
        this(serverIp, serverPort, 0.0);
    }

    public FacilityBookingGUI(String serverIp, int serverPort, double dropRate) {
        this.network = new NetworkClient(serverIp, serverPort, dropRate);
        
        // Setup main window
        setTitle("Facility Booking System - Client");
        setSize(900, 700);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);
        
        // Create interface
        createWidgets();
        
        // Add window listener to close network on exit
        addWindowListener(new java.awt.event.WindowAdapter() {
            @Override
            public void windowClosing(java.awt.event.WindowEvent windowEvent) {
                network.close();
            }
        });
    }
    
    private void createWidgets() {
        // Main panel
        JPanel mainPanel = new JPanel(new BorderLayout());
        mainPanel.setBackground(BACKGROUND_COLOR);
        
        // Top bar
        JPanel topBar = new JPanel(new BorderLayout());
        topBar.setBackground(PRIMARY_COLOR);
        topBar.setPreferredSize(new Dimension(900, 56));
        topBar.setBorder(new EmptyBorder(8, 24, 8, 24));
        
        JLabel titleLabel = new JLabel("Facility Booking System");
        titleLabel.setFont(new Font("Segoe UI", Font.BOLD, 18));
        titleLabel.setForeground(Color.WHITE);
        topBar.add(titleLabel, BorderLayout.WEST);
        
        JLabel serverLabel = new JLabel("Server: " + network.getServerIp() + ":" + network.getServerPort());
        serverLabel.setFont(new Font("Segoe UI", Font.PLAIN, 11));
        serverLabel.setForeground(new Color(201, 173, 167));
        topBar.add(serverLabel, BorderLayout.EAST);
        
        mainPanel.add(topBar, BorderLayout.NORTH);
        
        // Tabbed pane for content
        tabbedPane = new JTabbedPane();
        tabbedPane.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        
        // Create tabs
        tabbedPane.addTab("Query Availability", createQueryTab());
        tabbedPane.addTab("Book Facility", createBookTab());
        tabbedPane.addTab("Change Booking", createChangeTab());
        tabbedPane.addTab("Operations", createOperationsTab());
        
        mainPanel.add(tabbedPane, BorderLayout.CENTER);
        
        // Log area
        JPanel logPanel = new JPanel(new BorderLayout());
        logPanel.setBackground(PRIMARY_COLOR);
        logPanel.setPreferredSize(new Dimension(900, 120));
        logPanel.setBorder(new EmptyBorder(8, 16, 12, 16));
        
        JLabel logLabel = new JLabel("Log");
        logLabel.setFont(new Font("Segoe UI", Font.BOLD, 11));
        logLabel.setForeground(Color.WHITE);
        logPanel.add(logLabel, BorderLayout.NORTH);
        
        logText = new JTextArea();
        logText.setEditable(false);
        logText.setFont(new Font("Consolas", Font.PLAIN, 10));
        logText.setBackground(new Color(35, 36, 58));
        logText.setForeground(new Color(224, 225, 221));
        JScrollPane logScroll = new JScrollPane(logText);
        logPanel.add(logScroll, BorderLayout.CENTER);
        
        mainPanel.add(logPanel, BorderLayout.SOUTH);
        
        add(mainPanel);
        
        log("Client started");
    }
    
    private JPanel createQueryTab() {
        JPanel panel = new JPanel();
        panel.setLayout(new GridBagLayout());
        panel.setBackground(Color.WHITE);
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.insets = new Insets(6, 6, 6, 6);
        gbc.anchor = GridBagConstraints.WEST;
        
        // Title
        JLabel title = new JLabel("Query Facility Availability");
        title.setFont(new Font("Segoe UI", Font.BOLD, 15));
        gbc.gridx = 0;
        gbc.gridy = 0;
        gbc.gridwidth = 2;
        gbc.insets = new Insets(18, 24, 8, 24);
        panel.add(title, gbc);
        
        gbc.gridwidth = 1;
        gbc.insets = new Insets(6, 24, 6, 8);
        
        // Facility name
        gbc.gridy = 1;
        gbc.gridx = 0;
        gbc.anchor = GridBagConstraints.EAST;
        panel.add(new JLabel("Facility Name:"), gbc);
        
        gbc.gridx = 1;
        gbc.anchor = GridBagConstraints.WEST;
        queryFacility = new JComboBox<>(new String[]{
            "Conference_Room_A", "Conference_Room_B", "Lab_101", "Lab_102", "Auditorium"
        });
        queryFacility.setPreferredSize(new Dimension(250, 25));
        panel.add(queryFacility, gbc);
        
        // Query days
        gbc.gridy = 2;
        gbc.gridx = 0;
        gbc.anchor = GridBagConstraints.EAST;
        panel.add(new JLabel("Query Days (comma separated, 0=today):"), gbc);
        
        gbc.gridx = 1;
        gbc.anchor = GridBagConstraints.WEST;
        queryDays = new JTextField("0,1,2", 20);
        panel.add(queryDays, gbc);
        
        // Query button
        gbc.gridy = 3;
        gbc.gridx = 0;
        gbc.gridwidth = 2;
        gbc.anchor = GridBagConstraints.CENTER;
        gbc.insets = new Insets(16, 6, 16, 6);
        JButton queryButton = createStyledButton("Query");
        queryButton.addActionListener(e -> queryAvailability());
        panel.add(queryButton, gbc);
        
        // Results
        gbc.gridy = 4;
        gbc.gridx = 0;
        gbc.anchor = GridBagConstraints.WEST;
        gbc.insets = new Insets(8, 24, 0, 8);
        panel.add(new JLabel("Available Time Slots:"), gbc);
        
        gbc.gridy = 5;
        gbc.gridwidth = 2;
        gbc.fill = GridBagConstraints.BOTH;
        gbc.weightx = 1.0;
        gbc.weighty = 1.0;
        gbc.insets = new Insets(0, 24, 18, 24);
        queryResult = new JTextArea(10, 60);
        queryResult.setEditable(false);
        queryResult.setFont(new Font("Consolas", Font.PLAIN, 10));
        queryResult.setBackground(BACKGROUND_COLOR);
        JScrollPane scrollPane = new JScrollPane(queryResult);
        panel.add(scrollPane, gbc);
        
        return panel;
    }
    
    private JPanel createBookTab() {
        JPanel panel = new JPanel();
        panel.setLayout(new GridBagLayout());
        panel.setBackground(Color.WHITE);
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.insets = new Insets(6, 6, 6, 6);
        gbc.anchor = GridBagConstraints.WEST;
        
        // Title
        JLabel title = new JLabel("Book Facility");
        title.setFont(new Font("Segoe UI", Font.BOLD, 15));
        gbc.gridx = 0;
        gbc.gridy = 0;
        gbc.gridwidth = 2;
        gbc.insets = new Insets(18, 24, 8, 24);
        panel.add(title, gbc);
        
        gbc.gridwidth = 1;
        gbc.insets = new Insets(6, 24, 6, 8);
        
        // Facility name
        gbc.gridy = 1;
        gbc.gridx = 0;
        gbc.anchor = GridBagConstraints.EAST;
        panel.add(new JLabel("Facility Name:"), gbc);
        
        gbc.gridx = 1;
        gbc.anchor = GridBagConstraints.WEST;
        bookFacility = new JComboBox<>(new String[]{
            "Conference_Room_A", "Conference_Room_B", "Lab_101", "Lab_102", "Auditorium"
        });
        bookFacility.setPreferredSize(new Dimension(250, 25));
        panel.add(bookFacility, gbc);
        
        // Date
        gbc.gridy = 2;
        gbc.gridx = 0;
        gbc.anchor = GridBagConstraints.EAST;
        panel.add(new JLabel("Date (YYYY-MM-DD):"), gbc);
        
        gbc.gridx = 1;
        gbc.anchor = GridBagConstraints.WEST;
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
        bookDate = new JTextField(sdf.format(new Date()), 20);
        panel.add(bookDate, gbc);
        
        // Time
        gbc.gridy = 3;
        gbc.gridx = 0;
        gbc.anchor = GridBagConstraints.EAST;
        panel.add(new JLabel("Start Time (HH:MM):"), gbc);
        
        gbc.gridx = 1;
        gbc.anchor = GridBagConstraints.WEST;
        bookTime = new JTextField("09:00", 20);
        panel.add(bookTime, gbc);
        
        // Duration
        gbc.gridy = 4;
        gbc.gridx = 0;
        gbc.anchor = GridBagConstraints.EAST;
        panel.add(new JLabel("Duration (hours):"), gbc);
        
        gbc.gridx = 1;
        gbc.anchor = GridBagConstraints.WEST;
        bookDuration = new JTextField("1", 20);
        panel.add(bookDuration, gbc);
        
        // Book button
        gbc.gridy = 5;
        gbc.gridx = 0;
        gbc.gridwidth = 2;
        gbc.anchor = GridBagConstraints.CENTER;
        gbc.insets = new Insets(16, 6, 16, 6);
        JButton bookButton = createStyledButton("Book Facility");
        bookButton.addActionListener(e -> bookFacility());
        panel.add(bookButton, gbc);
        
        // Results
        gbc.gridy = 6;
        gbc.gridx = 0;
        gbc.anchor = GridBagConstraints.WEST;
        gbc.insets = new Insets(8, 24, 0, 8);
        panel.add(new JLabel("Booking Result:"), gbc);
        
        gbc.gridy = 7;
        gbc.gridwidth = 2;
        gbc.fill = GridBagConstraints.BOTH;
        gbc.weightx = 1.0;
        gbc.weighty = 1.0;
        gbc.insets = new Insets(0, 24, 18, 24);
        bookResult = new JTextArea(8, 60);
        bookResult.setEditable(false);
        bookResult.setFont(new Font("Consolas", Font.PLAIN, 10));
        bookResult.setBackground(BACKGROUND_COLOR);
        JScrollPane scrollPane = new JScrollPane(bookResult);
        panel.add(scrollPane, gbc);
        
        return panel;
    }
    
    private JPanel createChangeTab() {
        JPanel panel = new JPanel();
        panel.setLayout(new GridBagLayout());
        panel.setBackground(Color.WHITE);
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.insets = new Insets(6, 6, 6, 6);
        gbc.anchor = GridBagConstraints.WEST;
        
        // Title
        JLabel title = new JLabel("Change Booking");
        title.setFont(new Font("Segoe UI", Font.BOLD, 15));
        gbc.gridx = 0;
        gbc.gridy = 0;
        gbc.gridwidth = 2;
        gbc.insets = new Insets(18, 24, 8, 24);
        panel.add(title, gbc);
        
        gbc.gridwidth = 1;
        gbc.insets = new Insets(6, 24, 6, 8);
        
        // Confirmation ID
        gbc.gridy = 1;
        gbc.gridx = 0;
        gbc.anchor = GridBagConstraints.EAST;
        panel.add(new JLabel("Confirmation ID:"), gbc);
        
        gbc.gridx = 1;
        gbc.anchor = GridBagConstraints.WEST;
        changeId = new JTextField(20);
        panel.add(changeId, gbc);
        
        // Time offset
        gbc.gridy = 2;
        gbc.gridx = 0;
        gbc.anchor = GridBagConstraints.EAST;
        panel.add(new JLabel("Time Offset (minutes):"), gbc);
        
        gbc.gridx = 1;
        gbc.anchor = GridBagConstraints.WEST;
        changeOffset = new JTextField("30", 20);
        panel.add(changeOffset, gbc);
        
        // Help text
        gbc.gridy = 3;
        gbc.gridx = 1;
        JLabel helpText = new JLabel("(Positive for later, negative for earlier)");
        helpText.setFont(new Font("Segoe UI", Font.ITALIC, 9));
        helpText.setForeground(Color.GRAY);
        panel.add(helpText, gbc);
        
        // Change button
        gbc.gridy = 4;
        gbc.gridx = 0;
        gbc.gridwidth = 2;
        gbc.anchor = GridBagConstraints.CENTER;
        gbc.insets = new Insets(16, 6, 16, 6);
        JButton changeButton = createStyledButton("Change Booking");
        changeButton.addActionListener(e -> changeBooking());
        panel.add(changeButton, gbc);
        
        // Results
        gbc.gridy = 5;
        gbc.gridx = 0;
        gbc.anchor = GridBagConstraints.WEST;
        gbc.insets = new Insets(8, 24, 0, 8);
        panel.add(new JLabel("Change Result:"), gbc);
        
        gbc.gridy = 6;
        gbc.gridwidth = 2;
        gbc.fill = GridBagConstraints.BOTH;
        gbc.weightx = 1.0;
        gbc.weighty = 1.0;
        gbc.insets = new Insets(0, 24, 18, 24);
        changeResult = new JTextArea(8, 60);
        changeResult.setEditable(false);
        changeResult.setFont(new Font("Consolas", Font.PLAIN, 10));
        changeResult.setBackground(BACKGROUND_COLOR);
        JScrollPane scrollPane = new JScrollPane(changeResult);
        panel.add(scrollPane, gbc);
        
        return panel;
    }
    
    private JPanel createOperationsTab() {
        JPanel panel = new JPanel();
        panel.setLayout(new GridBagLayout());
        panel.setBackground(Color.WHITE);
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.insets = new Insets(6, 6, 6, 6);
        gbc.anchor = GridBagConstraints.WEST;
        
        // Title
        JLabel title = new JLabel("Additional Operations");
        title.setFont(new Font("Segoe UI", Font.BOLD, 15));
        gbc.gridx = 0;
        gbc.gridy = 0;
        gbc.gridwidth = 2;
        gbc.insets = new Insets(18, 24, 8, 24);
        panel.add(title, gbc);
        
        // Get last booking time section
        JLabel lastBookingTitle = new JLabel("Get Last Booking Time (Idempotent)");
        lastBookingTitle.setFont(new Font("Segoe UI", Font.BOLD, 12));
        lastBookingTitle.setForeground(SECONDARY_COLOR);
        gbc.gridy = 1;
        gbc.insets = new Insets(12, 24, 6, 24);
        panel.add(lastBookingTitle, gbc);
        
        gbc.gridwidth = 1;
        gbc.insets = new Insets(6, 24, 6, 8);
        
        gbc.gridy = 2;
        gbc.gridx = 0;
        gbc.anchor = GridBagConstraints.EAST;
        panel.add(new JLabel("Facility Name:"), gbc);
        
        gbc.gridx = 1;
        gbc.anchor = GridBagConstraints.WEST;
        lastTimeFacility = new JComboBox<>(new String[]{
            "Conference_Room_A", "Conference_Room_B", "Lab_101", "Lab_102", "Auditorium"
        });
        lastTimeFacility.setPreferredSize(new Dimension(250, 25));
        panel.add(lastTimeFacility, gbc);
        
        gbc.gridy = 3;
        gbc.gridx = 0;
        gbc.gridwidth = 2;
        gbc.anchor = GridBagConstraints.CENTER;
        gbc.insets = new Insets(10, 6, 10, 6);
        JButton lastTimeButton = createSecondaryButton("Query Last Booking Time");
        lastTimeButton.addActionListener(e -> getLastBookingTime());
        panel.add(lastTimeButton, gbc);
        
        // Separator
        gbc.gridy = 4;
        gbc.fill = GridBagConstraints.HORIZONTAL;
        gbc.insets = new Insets(12, 24, 12, 24);
        panel.add(new JSeparator(), gbc);
        
        // Extend booking section
        JLabel extendTitle = new JLabel("Extend Booking (Non-Idempotent)");
        extendTitle.setFont(new Font("Segoe UI", Font.BOLD, 12));
        extendTitle.setForeground(SECONDARY_COLOR);
        gbc.gridy = 5;
        gbc.fill = GridBagConstraints.NONE;
        gbc.insets = new Insets(6, 24, 6, 24);
        panel.add(extendTitle, gbc);
        
        gbc.gridwidth = 1;
        gbc.insets = new Insets(6, 24, 6, 8);
        
        gbc.gridy = 6;
        gbc.gridx = 0;
        gbc.anchor = GridBagConstraints.EAST;
        panel.add(new JLabel("Confirmation ID:"), gbc);
        
        gbc.gridx = 1;
        gbc.anchor = GridBagConstraints.WEST;
        extendId = new JTextField(20);
        panel.add(extendId, gbc);
        
        gbc.gridy = 7;
        gbc.gridx = 0;
        gbc.anchor = GridBagConstraints.EAST;
        panel.add(new JLabel("Extension Time (minutes):"), gbc);
        
        gbc.gridx = 1;
        gbc.anchor = GridBagConstraints.WEST;
        extendMinutes = new JTextField("30", 20);
        panel.add(extendMinutes, gbc);
        
        gbc.gridy = 8;
        gbc.gridx = 0;
        gbc.gridwidth = 2;
        gbc.anchor = GridBagConstraints.CENTER;
        gbc.insets = new Insets(10, 6, 10, 6);
        JButton extendButton = createSecondaryButton("Extend Booking");
        extendButton.addActionListener(e -> extendBooking());
        panel.add(extendButton, gbc);
        
        // Results
        gbc.gridy = 9;
        gbc.gridx = 0;
        gbc.anchor = GridBagConstraints.WEST;
        gbc.insets = new Insets(8, 24, 0, 8);
        panel.add(new JLabel("Operation Result:"), gbc);
        
        gbc.gridy = 10;
        gbc.gridwidth = 2;
        gbc.fill = GridBagConstraints.BOTH;
        gbc.weightx = 1.0;
        gbc.weighty = 1.0;
        gbc.insets = new Insets(0, 24, 18, 24);
        opsResult = new JTextArea(8, 60);
        opsResult.setEditable(false);
        opsResult.setFont(new Font("Consolas", Font.PLAIN, 10));
        opsResult.setBackground(BACKGROUND_COLOR);
        JScrollPane scrollPane = new JScrollPane(opsResult);
        panel.add(scrollPane, gbc);
        
        return panel;
    }
    
    private JButton createStyledButton(String text) {
        JButton button = new JButton(text);
        button.setFont(new Font("Segoe UI", Font.BOLD, 12));
        button.setBackground(SECONDARY_COLOR);
        button.setForeground(Color.WHITE);
        button.setOpaque(true);  // Required for background color on macOS
        button.setBorderPainted(true);
        button.setFocusPainted(false);
        button.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createLineBorder(SECONDARY_COLOR, 2),
            BorderFactory.createEmptyBorder(5, 15, 5, 15)
        ));
        button.setPreferredSize(new Dimension(150, 35));
        button.setCursor(new Cursor(Cursor.HAND_CURSOR));
        // Add hover effect
        button.addMouseListener(new java.awt.event.MouseAdapter() {
            public void mouseEntered(java.awt.event.MouseEvent evt) {
                button.setBackground(ACCENT_COLOR);
            }
            public void mouseExited(java.awt.event.MouseEvent evt) {
                button.setBackground(SECONDARY_COLOR);
            }
        });
        return button;
    }
    
    private JButton createSecondaryButton(String text) {
        JButton button = new JButton(text);
        button.setFont(new Font("Segoe UI", Font.BOLD, 11));
        button.setBackground(new Color(108, 117, 125));
        button.setForeground(Color.WHITE);
        button.setOpaque(true);  // Required for background color on macOS
        button.setBorderPainted(true);
        button.setFocusPainted(false);
        button.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createLineBorder(new Color(108, 117, 125), 2),
            BorderFactory.createEmptyBorder(4, 12, 4, 12)
        ));
        button.setPreferredSize(new Dimension(200, 30));
        button.setCursor(new Cursor(Cursor.HAND_CURSOR));
        // Add hover effect
        button.addMouseListener(new java.awt.event.MouseAdapter() {
            public void mouseEntered(java.awt.event.MouseEvent evt) {
                button.setBackground(new Color(90, 98, 104));
            }
            public void mouseExited(java.awt.event.MouseEvent evt) {
                button.setBackground(new Color(108, 117, 125));
            }
        });
        return button;
    }
    
    private void log(String message) {
        SwingUtilities.invokeLater(() -> {
            SimpleDateFormat sdf = new SimpleDateFormat("HH:mm:ss");
            String timestamp = sdf.format(new Date());
            logText.append("[" + timestamp + "] " + message + "\n");
            logText.setCaretPosition(logText.getDocument().getLength());
        });
    }
    
    private void queryAvailability() {
        new Thread(() -> {
            try {
                String facilityName = (String) queryFacility.getSelectedItem();
                String daysInput = queryDays.getText().trim();
                String[] dayStrings = daysInput.split(",");
                int[] days = new int[dayStrings.length];
                for (int i = 0; i < dayStrings.length; i++) {
                    days[i] = Integer.parseInt(dayStrings[i].trim());
                }
                
                log("Querying availability for " + facilityName + "...");
                
                // Build request
                ByteBuffer request = new ByteBuffer();
                int requestId = network.getNextRequestId();
                request.writeUInt32(requestId);
                request.writeUInt8(MessageTypes.MSG_QUERY_AVAILABILITY);
                
                ByteBuffer payload = new ByteBuffer();
                payload.writeString(facilityName);
                payload.writeUInt16(days.length);
                for (int day : days) {
                    payload.writeUInt32(day);
                }
                
                request.writeUInt16(payload.size());
                request.write(payload.getData());
                
                // Send request
                byte[] responseData = network.sendRequest(request.getData());
                if (responseData == null) {
                    SwingUtilities.invokeLater(() -> {
                        queryResult.setText("Request timeout\n");
                    });
                    log("Request timeout");
                    return;
                }
                
                // Parse response
                ByteBuffer response = new ByteBuffer(responseData);
                long respRequestId = response.readUInt32();
                int status = response.readUInt8();
                
                if (status == MessageTypes.MSG_RESPONSE_ERROR) {
                    String errorMsg = response.readString();
                    SwingUtilities.invokeLater(() -> {
                        queryResult.setText("Error: " + errorMsg + "\n");
                    });
                    log("Error: " + errorMsg);
                    return;
                }
                
                // Read available time slots
                int numSlots = response.readUInt16();
                StringBuilder resultText = new StringBuilder();
                resultText.append("Found ").append(numSlots).append(" available time slots:\n\n");
                
                SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm");
                SimpleDateFormat timeSdf = new SimpleDateFormat("HH:mm");
                
                for (int i = 0; i < numSlots; i++) {
                    long startTime = response.readTime();
                    long endTime = response.readTime();
                    
                    Date startDate = new Date(startTime * 1000);
                    Date endDate = new Date(endTime * 1000);
                    
                    resultText.append(String.format("%d. %s to %s\n", 
                        i + 1, sdf.format(startDate), timeSdf.format(endDate)));
                }
                
                SwingUtilities.invokeLater(() -> {
                    queryResult.setText(resultText.toString());
                });
                log("Query successful, found " + numSlots + " time slots");
                
            } catch (Exception e) {
                String error = "Query failed: " + e.getMessage();
                SwingUtilities.invokeLater(() -> {
                    JOptionPane.showMessageDialog(this, error, "Error", JOptionPane.ERROR_MESSAGE);
                });
                log("Error: " + e.getMessage());
                e.printStackTrace();
            }
        }).start();
    }
    
    private void bookFacility() {
        new Thread(() -> {
            try {
                String facilityName = (String) bookFacility.getSelectedItem();
                String dateStr = bookDate.getText().trim();
                String timeStr = bookTime.getText().trim();
                double durationHours = Double.parseDouble(bookDuration.getText().trim());
                
                // Parse time
                SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm");
                Date startDate = sdf.parse(dateStr + " " + timeStr);
                long startTime = startDate.getTime() / 1000;
                long endTime = startTime + (long)(durationHours * 3600);
                
                log("Booking " + facilityName + "...");
                
                // Build request
                ByteBuffer request = new ByteBuffer();
                int requestId = network.getNextRequestId();
                request.writeUInt32(requestId);
                request.writeUInt8(MessageTypes.MSG_BOOK_FACILITY);
                
                ByteBuffer payload = new ByteBuffer();
                payload.writeString(facilityName);
                payload.writeTime(startTime);
                payload.writeTime(endTime);
                
                request.writeUInt16(payload.size());
                request.write(payload.getData());
                
                // Send request
                byte[] responseData = network.sendRequest(request.getData());
                if (responseData == null) {
                    SwingUtilities.invokeLater(() -> {
                        bookResult.setText("Request timeout\n");
                    });
                    log("Request timeout");
                    return;
                }
                
                // Parse response
                ByteBuffer response = new ByteBuffer(responseData);
                long respRequestId = response.readUInt32();
                int status = response.readUInt8();
                
                if (status == MessageTypes.MSG_RESPONSE_ERROR) {
                    String errorMsg = response.readString();
                    SwingUtilities.invokeLater(() -> {
                        bookResult.setText("Booking failed: " + errorMsg + "\n");
                    });
                    log("Booking failed: " + errorMsg);
                    return;
                }
                
                // Read confirmation ID
                long confirmationId = response.readUInt32();
                
                SimpleDateFormat displaySdf = new SimpleDateFormat("yyyy-MM-dd HH:mm");
                SimpleDateFormat timeSdf = new SimpleDateFormat("HH:mm");
                
                StringBuilder resultText = new StringBuilder();
                resultText.append("✓ Booking Success!\n\n");
                resultText.append("Confirmation ID: ").append(confirmationId).append("\n");
                resultText.append("Facility: ").append(facilityName).append("\n");
                resultText.append("Time: ").append(displaySdf.format(startDate))
                    .append(" to ").append(timeSdf.format(new Date(endTime * 1000))).append("\n");
                
                SwingUtilities.invokeLater(() -> {
                    bookResult.setText(resultText.toString());
                    JOptionPane.showMessageDialog(this, 
                        "Booking Success! Confirmation ID: " + confirmationId,
                        "Success", JOptionPane.INFORMATION_MESSAGE);
                });
                log("Booking Success, Confirmation ID: " + confirmationId);
                
            } catch (Exception e) {
                String error = "Booking failed: " + e.getMessage();
                SwingUtilities.invokeLater(() -> {
                    JOptionPane.showMessageDialog(this, error, "Error", JOptionPane.ERROR_MESSAGE);
                });
                log("Error: " + e.getMessage());
                e.printStackTrace();
            }
        }).start();
    }
    
    private void changeBooking() {
        new Thread(() -> {
            try {
                long confirmationId = Long.parseLong(changeId.getText().trim());
                int offsetMinutes = Integer.parseInt(changeOffset.getText().trim());
                
                log("Change booking ID " + confirmationId + "...");
                
                // Build request
                ByteBuffer request = new ByteBuffer();
                int requestId = network.getNextRequestId();
                request.writeUInt32(requestId);
                request.writeUInt8(MessageTypes.MSG_CHANGE_BOOKING);
                
                ByteBuffer payload = new ByteBuffer();
                payload.writeUInt32(confirmationId);
                payload.writeUInt32(offsetMinutes & 0xFFFFFFFFL);
                
                request.writeUInt16(payload.size());
                request.write(payload.getData());
                
                // Send request
                byte[] responseData = network.sendRequest(request.getData());
                if (responseData == null) {
                    SwingUtilities.invokeLater(() -> {
                        changeResult.setText("Request timeout\n");
                    });
                    log("Request timeout");
                    return;
                }
                
                // Parse response
                ByteBuffer response = new ByteBuffer(responseData);
                long respRequestId = response.readUInt32();
                int status = response.readUInt8();
                
                if (status == MessageTypes.MSG_RESPONSE_ERROR) {
                    String errorMsg = response.readString();
                    SwingUtilities.invokeLater(() -> {
                        changeResult.setText("Change failed: " + errorMsg + "\n");
                    });
                    log("Change failed: " + errorMsg);
                    return;
                }
                
                String message = response.readString();
                SwingUtilities.invokeLater(() -> {
                    changeResult.setText("✓ " + message + "\n");
                    JOptionPane.showMessageDialog(this, message, "Success", JOptionPane.INFORMATION_MESSAGE);
                });
                log("Booking changed successfully");
                
            } catch (Exception e) {
                String error = "Change failed: " + e.getMessage();
                SwingUtilities.invokeLater(() -> {
                    JOptionPane.showMessageDialog(this, error, "Error", JOptionPane.ERROR_MESSAGE);
                });
                log("Error: " + e.getMessage());
                e.printStackTrace();
            }
        }).start();
    }
    
    private void getLastBookingTime() {
        new Thread(() -> {
            try {
                String facilityName = (String) lastTimeFacility.getSelectedItem();
                
                log("Querying " + facilityName + " last booking time...");
                
                // Build request
                ByteBuffer request = new ByteBuffer();
                int requestId = network.getNextRequestId();
                request.writeUInt32(requestId);
                request.writeUInt8(MessageTypes.MSG_GET_LAST_BOOKING_TIME);
                
                ByteBuffer payload = new ByteBuffer();
                payload.writeString(facilityName);
                
                request.writeUInt16(payload.size());
                request.write(payload.getData());
                
                // Send request
                byte[] responseData = network.sendRequest(request.getData());
                if (responseData == null) {
                    SwingUtilities.invokeLater(() -> {
                        opsResult.setText("Request timeout\n");
                    });
                    log("Request timeout");
                    return;
                }
                
                // Parse response
                ByteBuffer response = new ByteBuffer(responseData);
                long respRequestId = response.readUInt32();
                int status = response.readUInt8();
                
                if (status == MessageTypes.MSG_RESPONSE_ERROR) {
                    String errorMsg = response.readString();
                    SwingUtilities.invokeLater(() -> {
                        opsResult.setText("Error: " + errorMsg + "\n");
                    });
                    log("Error: " + errorMsg);
                    return;
                }
                
                long lastTime = response.readTime();
                String message = response.readString();
                
                StringBuilder resultText = new StringBuilder();
                resultText.append("Facility: ").append(facilityName).append("\n");
                
                if (lastTime == 0) {
                    resultText.append(message).append("\n");
                } else {
                    SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
                    Date lastDate = new Date(lastTime * 1000);
                    resultText.append("Last booking end time: ").append(sdf.format(lastDate)).append("\n");
                    resultText.append("Status: ").append(message).append("\n");
                }
                
                SwingUtilities.invokeLater(() -> {
                    opsResult.setText(resultText.toString());
                });
                log("Querying Success");
                
            } catch (Exception e) {
                String error = "Query failed: " + e.getMessage();
                SwingUtilities.invokeLater(() -> {
                    JOptionPane.showMessageDialog(this, error, "Error", JOptionPane.ERROR_MESSAGE);
                });
                log("Error: " + e.getMessage());
                e.printStackTrace();
            }
        }).start();
    }
    
    private void extendBooking() {
        new Thread(() -> {
            try {
                long confirmationId = Long.parseLong(extendId.getText().trim());
                int minutesToExtend = Integer.parseInt(extendMinutes.getText().trim());
                
                log("Extend booking ID " + confirmationId + "...");
                
                // Build request
                ByteBuffer request = new ByteBuffer();
                int requestId = network.getNextRequestId();
                request.writeUInt32(requestId);
                request.writeUInt8(MessageTypes.MSG_EXTEND_BOOKING);
                
                ByteBuffer payload = new ByteBuffer();
                payload.writeUInt32(confirmationId);
                payload.writeUInt32(minutesToExtend);
                
                request.writeUInt16(payload.size());
                request.write(payload.getData());
                
                // Send request
                byte[] responseData = network.sendRequest(request.getData());
                if (responseData == null) {
                    SwingUtilities.invokeLater(() -> {
                        opsResult.setText("Request timeout\n");
                    });
                    log("Request timeout");
                    return;
                }
                
                // Parse response
                ByteBuffer response = new ByteBuffer(responseData);
                long respRequestId = response.readUInt32();
                int status = response.readUInt8();
                
                if (status == MessageTypes.MSG_RESPONSE_ERROR) {
                    String errorMsg = response.readString();
                    SwingUtilities.invokeLater(() -> {
                        opsResult.setText("Extension failed: " + errorMsg + "\n");
                    });
                    log("Extension failed: " + errorMsg);
                    return;
                }
                
                long newEndTime = response.readTime();
                String message = response.readString();
                
                SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
                Date newEndDate = new Date(newEndTime * 1000);
                
                StringBuilder resultText = new StringBuilder();
                resultText.append("✓ ").append(message).append("\n");
                resultText.append("New end time: ").append(sdf.format(newEndDate)).append("\n");
                
                SwingUtilities.invokeLater(() -> {
                    opsResult.setText(resultText.toString());
                    JOptionPane.showMessageDialog(this, message, "Success", JOptionPane.INFORMATION_MESSAGE);
                });
                log("Extension successful");
                
            } catch (Exception e) {
                String error = "Extension failed: " + e.getMessage();
                SwingUtilities.invokeLater(() -> {
                    JOptionPane.showMessageDialog(this, error, "Error", JOptionPane.ERROR_MESSAGE);
                });
                log("Error: " + e.getMessage());
                e.printStackTrace();
            }
        }).start();
    }
    
    public static void main(String[] args) {
        String serverIp = "8.148.159.175";
        int serverPort = 8080;
        double dropRate = 0.0;
        
        // Parse command line arguments
        for (int i = 0; i < args.length; i++) {
            if (args[i].equals("--drop-rate")) {
                if (i + 1 < args.length) {
                    try {
                        dropRate = Double.parseDouble(args[++i]);
                        if (dropRate < 0.0 || dropRate > 1.0) {
                            System.err.println("Error: drop-rate must be between 0.0 and 1.0");
                            System.exit(1);
                        }
                    } catch (NumberFormatException e) {
                        System.err.println("Error: drop-rate must be a number");
                        System.exit(1);
                    }
                } else {
                    System.err.println("Error: --drop-rate requires a value");
                    System.exit(1);
                }
            } else if (args[i].startsWith("--")) {
                System.err.println("Unknown option: " + args[i]);
                System.err.println("Usage: java FacilityBookingGUI [server_ip] [server_port] [--drop-rate rate]");
                System.exit(1);
            } else {
                // Positional arguments
                if (i == 0) {
                    serverIp = args[i];
                } else if (i == 1) {
                    try {
                        serverPort = Integer.parseInt(args[i]);
                    } catch (NumberFormatException e) {
                        System.err.println("Error: server_port must be a number");
                        System.exit(1);
                    }
                } else {
                    System.err.println("Too many positional arguments");
                    System.err.println("Usage: java FacilityBookingGUI [server_ip] [server_port] [--drop-rate rate]");
                    System.exit(1);
                }
            }
        }
        
        System.out.println("Connecting to server: " + serverIp + ":" + serverPort);
        if (dropRate > 0.0) {
            System.out.println("Packet drop rate: " + dropRate);
        }
        
        // Set look and feel
        try {
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        } catch (Exception e) {
            e.printStackTrace();
        }
        
        SwingUtilities.invokeLater(() -> {
            FacilityBookingGUI gui = new FacilityBookingGUI(serverIp, serverPort, dropRate);
            gui.setVisible(true);
        });
    }
}
