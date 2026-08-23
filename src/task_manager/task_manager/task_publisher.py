import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class TaskPublisher(Node):
    def __init__(self):
        super().__init__('task_publisher')
        self.publisher_ = self.create_publisher(String, 'factory/task', 10)
        self.timer = self.create_timer(2.0, self.publish_task)

    def publish_task(self):
        msg = String()
        msg.data = 'transport Station_A -> Station_B'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Published: {msg.data}')

def main():
    rclpy.init()
    node = TaskPublisher()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
