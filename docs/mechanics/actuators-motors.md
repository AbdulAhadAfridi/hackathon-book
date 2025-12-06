---
title: Actuators Motors
description: Description for Actuators Motors chapter.
---

```mermaid
graph TD
    A[Robot Joint] --> B{Actuator System};
    B --> C{Motor};
    B --> D{Transmission};

    C --> C1[DC Motors];
    C1 --> C1a(Brushed DC);
    C1 --> C1b(Brushless DC);
    C --> C2[Stepper Motors];
    C --> C3[Servo Motors];

    D --> D1[Gearbox];
    D --> D2[Harmonic Drive];
    D --> D3[Cycloidal Drive];

    B --> E[Series Elastic Actuator (SEA)];
```

# Actuators & Motors: Bringing Robots to Life

While sensors provide humanoid robots with the ability to perceive, **actuators** are the components that enable them to move and interact physically with the world. Actuators convert energy (typically electrical) into mechanical force or motion, essentially serving as the robot's muscles. This chapter delves into the types of actuators and motors commonly employed in humanoid robotics and their operational principles.

## Motors: The Power Behind the Motion

The most common type of actuator in robotics is the electric motor. Different types of motors are chosen based on requirements for power, precision, speed, and size.

*   **DC Motors (Direct Current Motors)**: These are fundamental and widely used due to their simplicity and ease of control.
    *   **Brushed DC Motors**: Rely on brushes to deliver current to the motor windings. They are simple, robust, and inexpensive but suffer from wear and tear on the brushes, leading to a shorter lifespan and electrical noise.
    *   **Brushless DC (BLDC) Motors**: These motors use electronic commutation instead of brushes. They offer higher efficiency, longer lifespan, less noise, and better speed/torque control, making them increasingly popular in advanced robotics despite being more complex to control (requiring a motor controller/driver). BLDC motors are often the preferred choice for powerful and precise humanoid joints.

*   **Stepper Motors**: These motors move in discrete steps, making them excellent for precise positioning without the need for complex feedback mechanisms (though feedback is often added for verification). They are commonly used in applications requiring accurate indexing or rotation, but they can be less energy-efficient and prone to losing steps under heavy loads.

*   **Servo Motors**: A servo motor is not a specific motor type but rather a DC or BLDC motor integrated with a gear train, a position sensor (encoder/potentiometer), and an electronic control circuit (servo driver). This integrated package allows for precise control of angular position, velocity, and sometimes torque. They are ubiquitous in robotics due to their ease of use and high positional accuracy.

## Other Actuator Types

Beyond electric motors, other actuator technologies are sometimes employed in humanoid robots, particularly for specific applications where high force-to-weight ratios or compliance are critical.

*   **Hydraulic Actuators**: Use pressurized fluid to generate force. They offer extremely high power density (large forces from small actuators) and are commonly found in heavy-duty industrial robots. However, they are complex, messy (due to fluid leaks), and difficult to miniaturize for humanoid applications, typically reserved for research robots like Boston Dynamics' early hydraulic Atlas.

*   **Pneumatic Actuators**: Use compressed air. They are lightweight, simple, and can be very fast. However, they are generally less precise and harder to control for continuous, smooth motion compared to electric motors. They are more suited for gripper mechanisms or tasks requiring rapid, binary (on/off) movements.

*   **Series Elastic Actuators (SEAs)**: These are specialized actuators that incorporate a spring element (series elastic element) between the motor and the load. SEAs are not a motor type but an actuator design that enhances force control, compliance (the ability to yield to external forces), and energy storage. This compliance is crucial for safe human-robot interaction and for mimicking the spring-like properties of human muscles and tendons during dynamic movements like running and jumping.

## Gear Trains and Transmissions

Motors rarely connect directly to a robot's links. Instead, **gear trains** or **transmissions** are used to:

*   **Reduce Speed and Increase Torque**: Motors typically operate at high speeds and low torque. Gearboxes reduce the output speed while significantly increasing the torque, matching the requirements of a robot's joints.
*   **Improve Resolution**: By gearing down, the effective positional resolution of the joint increases.
*   **Backdrivability**: A crucial characteristic, especially in humanoids intended for human interaction, where the joints can be moved by external forces (e.g., a human guiding the robot's arm). High gear ratios can reduce backdrivability.

Common gear types include planetary gears, harmonic drives, and cycloidal drives, each offering different advantages in terms of compactness, backlash (play in the gears), and efficiency.

The selection of appropriate actuators and transmission systems is a critical design decision in humanoid robotics, directly impacting the robot's power, precision, speed, and safety characteristics. The trend is towards highly integrated, compact, and powerful electric servo actuators with sophisticated control, often incorporating series elastic elements, to achieve fluid, dynamic, and safe humanoid movement.

> **Citation Placeholder**: [Source: Robotics Actuator Design, 2024]
