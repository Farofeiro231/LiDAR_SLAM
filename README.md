# LiDAR_SLAM
Repository related to the development of a SLAM algorithm using a 2D LiDAR for my college's robotics club.

This project is intended to create a UKF code for the localization of a mobile robot. The sensor used with the filter is a 2D LiDAR.

I'm tackling this problem by using multiprocessing/multithreading to execute data capture and processing at the same time; 
graphical user interfaces (GUIs) for data visualization; and a Class-based approach to keep data from landmarks, the robot and the
system itself.

The core system has two main processes: the first acquires the sensor data and feeds into a multiprocessing queue for the second; the second is responsable for recovering the queue data and treating it (RANSAC), as well as plotting the points cloud. The second process has two inner threads, one for the ransac and data pprocessing, and the other for data visualization with the UI. The UI is developped using PyQt5, togheter with QChart and QScatterSeries.
