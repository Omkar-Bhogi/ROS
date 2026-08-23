import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class TaskListener(Node):
    def __init__(self):
        super().__init__('task_listener')
        self.subscription = self.create_subscription(
            String, 'factory/task', self.listener_callback, 10)

    def listener_callback(self, msg):
        self.get_logger().info(f'Received: {msg.data}')

def main():
    rclpy.init()
    node = TaskListener()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
