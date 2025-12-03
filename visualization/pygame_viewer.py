"""
Pygame可视化界面 - 提供图形化的仿真界面
"""

try:
    import pygame
    import pygame.gfxdraw

    PYGAME_AVAILABLE = True
except ImportError as e:
    print(f"Pygame未安装：{e}")
    PYGAME_AVAILABLE = False

from typing import Dict, List, Tuple


class PygameViewer:
    """Pygame可视化界面类"""

    def __init__(self, grid_size: int = 15, cell_size: int = 40, fps: int = 10):
        """
        初始化Pygame查看器
        Args:
            grid_size: 网格大小
            cell_size: 每个单元格的像素大小
            fps: 帧率
        """
        if not PYGAME_AVAILABLE:
            raise ImportError("Pygame未安装，请运行: pip install pygame")

        self.grid_size = grid_size
        self.cell_size = cell_size
        self.fps = fps

        # 窗口尺寸
        self.info_panel_width = 300
        self.grid_width = grid_size * cell_size
        self.grid_height = grid_size * cell_size
        self.window_width = self.grid_width + self.info_panel_width
        self.window_height = self.grid_height + 100  # 额外高度用于顶部信息栏

        # 颜色定义 - 现代化配色方案
        self.COLORS = {
            "background": (248, 249, 250),
            "grid_line": (220, 225, 230),
            "road": (255, 255, 255),
            "building": (108, 117, 125),
            "charging_station": (255, 193, 7),  # 琥珀色
            "charging_glow": (255, 235, 59),  # 充电站光晕
            "car_idle": (40, 167, 69),  # 现代绿
            "car_pickup": (13, 110, 253),  # 现代蓝
            "car_delivery": (253, 126, 20),  # 现代橙
            "car_charging": (255, 193, 7),  # 充电黄
            "car_low_battery": (220, 53, 69),  # 现代红
            "order_pickup": (13, 202, 240),  # 青色
            "order_delivery": (214, 51, 132),  # 品红
            "text": (33, 37, 41),
            "text_light": (108, 117, 125),
            "panel_bg": (255, 255, 255),
            "panel_shadow": (0, 0, 0, 30),
            "header_bg": (52, 58, 64),
            "header_text": (255, 255, 255),
            "success": (40, 167, 69),
            "warning": (255, 193, 7),
            "danger": (220, 53, 69),
        }

        # 初始化Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Campus Fleet AI - Multi-Agent Delivery System")
        self.clock = pygame.time.Clock()

        # 字体 - 使用系统字体支持中文
        self.font_large = self._get_font(28, bold=True)
        self.font_medium = self._get_font(20)
        self.font_small = self._get_font(16)

        self.running = True

    def _get_font(self, size: int, bold: bool = False):
        """
        获取支持中文的字体
        Args:
            size: 字体大小
            bold: 是否粗体
        Returns:
            pygame字体对象
        """
        # 尝试使用系统中文字体（macOS优先）
        chinese_fonts = [
            "PingFangSC-Regular",  # macOS (无空格)
            "PingFang SC",  # macOS
            "STHeiti",  # macOS 黑体
            "Heiti SC",  # macOS 黑体
            "Arial Unicode MS",  # macOS
            "Hiragino Sans GB",  # macOS
            "Microsoft YaHei",  # Windows
            "SimHei",  # Windows
            "WenQuanYi Micro Hei",  # Linux
            "Noto Sans CJK SC",  # Linux
        ]

        # 获取系统所有可用字体
        available_fonts = pygame.font.get_fonts()

        for font_name in chinese_fonts:
            # 尝试直接使用字体名称
            try:
                font = pygame.font.SysFont(font_name, size, bold=bold)
                if font:
                    # 测试渲染中文
                    test_surface = font.render("测试", True, (0, 0, 0))
                    if test_surface.get_width() > 0:
                        return font
            except Exception:
                pass

            # 尝试小写和无空格版本
            try:
                font_name_lower = font_name.lower().replace(" ", "")
                if font_name_lower in available_fonts:
                    font = pygame.font.SysFont(font_name, size, bold=bold)
                    if font:
                        return font
            except Exception:
                pass

        # 如果没有找到中文字体，使用默认字体
        print(f"⚠️  警告: 未找到合适的中文字体，使用默认字体")
        return pygame.font.Font(None, size)

    def handle_events(self) -> bool:
        """
        处理Pygame事件
        Returns:
            是否继续运行
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return False
        return True

    def draw_grid(self, grid: list, charging_stations: list):
        """
        绘制网格和障碍物
        Args:
            grid: 二维网格数组
            charging_stations: 充电站位置列表
        """
        offset_y = 100  # 顶部信息栏高度

        for i in range(self.grid_size):
            for j in range(self.grid_size):
                x = j * self.cell_size
                y = offset_y + i * self.cell_size

                # 绘制单元格背景
                if grid[i][j] == "#":
                    # 建筑物
                    color = self.COLORS["building"]
                else:
                    # 道路
                    color = self.COLORS["road"]

                pygame.draw.rect(self.screen, color, (x, y, self.cell_size, self.cell_size))

                # 绘制网格线
                pygame.draw.rect(
                    self.screen, self.COLORS["grid_line"], (x, y, self.cell_size, self.cell_size), 1
                )

        # 绘制充电站 - 带发光效果
        for pos in charging_stations:
            i, j = pos
            x = j * self.cell_size + self.cell_size // 2
            y = offset_y + i * self.cell_size + self.cell_size // 2

            # 绘制光晕效果（多层半透明圆）
            for radius_offset in range(3, 0, -1):
                alpha = 30 + radius_offset * 20
                s = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
                radius = self.cell_size // 3 + radius_offset * 3
                pygame.draw.circle(
                    s,
                    (*self.COLORS["charging_glow"], alpha),
                    (self.cell_size // 2, self.cell_size // 2),
                    radius,
                )
                self.screen.blit(s, (j * self.cell_size, offset_y + i * self.cell_size))

            # 绘制主体
            pygame.draw.circle(
                self.screen, self.COLORS["charging_station"], (x, y), self.cell_size // 3
            )

            # 绘制边框
            pygame.draw.circle(self.screen, (200, 150, 0), (x, y), self.cell_size // 3, 2)

            # 绘制闪电图标
            bolt_points = [
                (x - 4, y - 8),
                (x + 2, y - 2),
                (x - 2, y + 2),
                (x + 4, y + 8),
                (x, y + 2),
                (x + 2, y - 4),
            ]
            # pygame.draw.polygon(self.screen, (255, 255, 255), bolt_points)

    def draw_car(
        self, car_pos: Tuple[int, int], car_id: int, state: str, battery_percentage: float
    ):
        """
        绘制车辆
        Args:
            car_pos: 车辆位置 (x, y)
            car_id: 车辆ID
            state: 车辆状态
            battery_percentage: 电量百分比
        """
        offset_y = 100
        i, j = car_pos
        x = j * self.cell_size + self.cell_size // 2
        y = offset_y + i * self.cell_size + self.cell_size // 2

        # 计算半径
        radius = self.cell_size // 3

        # 根据状态选择颜色
        if state == "Charging" or state == "To Charger":
            color = self.COLORS["car_charging"]
        elif battery_percentage < 20:
            color = self.COLORS["car_low_battery"]
        elif state == "Idle":
            color = self.COLORS["car_idle"]
        elif state == "To Pickup":
            color = self.COLORS["car_pickup"]
        elif state == "Delivering":
            color = self.COLORS["car_delivery"]
        else:
            color = self.COLORS["car_idle"]

        # 绘制阴影
        shadow_surface = pygame.Surface((radius * 2 + 6, radius * 2 + 6), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surface, (0, 0, 0, 60), (radius + 3, radius + 3), radius + 2)
        self.screen.blit(shadow_surface, (x - radius - 3, y - radius - 2))

        # 绘制车辆主体（圆形）
        pygame.draw.circle(self.screen, color, (x, y), radius)

        # 绘制高光
        highlight_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            highlight_surface, (255, 255, 255, 80), (radius // 2, radius // 2), radius // 2
        )
        self.screen.blit(highlight_surface, (x - radius + radius // 2, y - radius + radius // 2))

        # 绘制边框
        pygame.draw.circle(self.screen, (0, 0, 0), (x, y), radius, 2)

        # 绘制车辆ID
        text = self.font_small.render(str(car_id), True, (255, 255, 255))
        text_rect = text.get_rect(center=(x, y - 5))
        self.screen.blit(text, text_rect)

        # 绘制电量条
        battery_bar_width = self.cell_size - 4
        battery_bar_height = 4
        battery_x = j * self.cell_size + 2
        battery_y = offset_y + (i + 1) * self.cell_size - 8

        # 电量条背景
        pygame.draw.rect(
            self.screen,
            (200, 200, 200),
            (battery_x, battery_y, battery_bar_width, battery_bar_height),
        )

        # 电量条填充
        fill_width = int(battery_bar_width * battery_percentage / 100)
        if battery_percentage > 50:
            battery_color = (0, 255, 0)
        elif battery_percentage > 20:
            battery_color = (255, 255, 0)
        else:
            battery_color = (255, 0, 0)

        pygame.draw.rect(
            self.screen, battery_color, (battery_x, battery_y, fill_width, battery_bar_height)
        )

    def draw_order_markers(self, orders: list):
        """
        绘制订单标记
        Args:
            orders: 订单列表
        """
        offset_y = 100

        for order in orders:
            # 绘制取货点标记
            pickup_i, pickup_j = order.pickup_point
            pickup_x = pickup_j * self.cell_size + self.cell_size // 4
            pickup_y = offset_y + pickup_i * self.cell_size + self.cell_size // 4

            pygame.draw.circle(self.screen, self.COLORS["order_pickup"], (pickup_x, pickup_y), 5)

            # 绘制配送点标记
            delivery_i, delivery_j = order.delivery_point
            delivery_x = delivery_j * self.cell_size + 3 * self.cell_size // 4
            delivery_y = offset_y + delivery_i * self.cell_size + 3 * self.cell_size // 4

            pygame.draw.circle(
                self.screen, self.COLORS["order_delivery"], (delivery_x, delivery_y), 5
            )

    def draw_info_panel(self, context):
        """
        绘制信息面板 - 现代化设计
        Args:
            context: 仿真上下文对象
        """
        panel_x = self.grid_width
        panel_y = 100
        panel_width = self.info_panel_width

        # 绘制面板背景和阴影
        shadow_surface = pygame.Surface((panel_width + 10, self.grid_height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 20), (5, 0, panel_width, self.grid_height))
        self.screen.blit(shadow_surface, (panel_x - 5, panel_y))

        pygame.draw.rect(
            self.screen, self.COLORS["panel_bg"], (panel_x, panel_y, panel_width, self.grid_height)
        )

        # 绘制垂直分隔线
        pygame.draw.line(
            self.screen,
            self.COLORS["grid_line"],
            (panel_x, panel_y),
            (panel_x, panel_y + self.grid_height),
            2,
        )

        # 绘制信息
        y_offset = panel_y + 20
        line_height = 28

        # 标题卡片
        card_y = y_offset
        pygame.draw.rect(
            self.screen,
            (240, 242, 245),
            (panel_x + 10, card_y, panel_width - 20, 40),
            border_radius=8,
        )
        title = self.font_medium.render("System Status", True, self.COLORS["text"])
        self.screen.blit(title, (panel_x + 20, card_y + 10))
        y_offset += 60

        # 统计信息卡片
        stats = [
            ("Step", str(context.current_step), self.COLORS["text_light"]),
            ("Completed", str(context.total_completed_orders), self.COLORS["success"]),
            (
                "Pending",
                str(context.order_agent.report()["pending_orders"]),
                self.COLORS["warning"],
            ),
        ]

        for label, value, color in stats:
            # 标签
            label_text = self.font_small.render(label + ":", True, self.COLORS["text_light"])
            self.screen.blit(label_text, (panel_x + 20, y_offset))

            # 数值
            value_text = self.font_medium.render(value, True, color)
            self.screen.blit(value_text, (panel_x + 150, y_offset - 2))

            y_offset += line_height

        y_offset += 15

        # 车辆状态卡片
        pygame.draw.rect(
            self.screen,
            (240, 242, 245),
            (panel_x + 10, y_offset, panel_width - 20, 30),
            border_radius=8,
        )
        vehicle_title = self.font_small.render("Vehicles", True, self.COLORS["text"])
        self.screen.blit(vehicle_title, (panel_x + 20, y_offset + 7))
        y_offset += 45

        for car in context.cars:
            # 车辆卡片背景
            card_height = 50
            pygame.draw.rect(
                self.screen,
                (248, 249, 250),
                (panel_x + 15, y_offset, panel_width - 30, card_height),
                border_radius=6,
            )

            # 车辆ID和状态
            car_label = self.font_small.render(f"Car {car.car_id}", True, self.COLORS["text"])
            self.screen.blit(car_label, (panel_x + 25, y_offset + 8))

            state_text = car.state.value[:6]
            state_label = self.font_small.render(state_text, True, self.COLORS["text_light"])
            self.screen.blit(state_label, (panel_x + 25, y_offset + 28))

            # 电量进度条
            battery_pct = car.get_battery_percentage()
            bar_x = panel_x + 150
            bar_y = y_offset + 15
            bar_width = 100
            bar_height = 18

            # 背景
            pygame.draw.rect(
                self.screen, (220, 220, 220), (bar_x, bar_y, bar_width, bar_height), border_radius=9
            )

            # 填充
            fill_width = int(bar_width * battery_pct / 100)
            if battery_pct > 50:
                bar_color = self.COLORS["success"]
            elif battery_pct > 20:
                bar_color = self.COLORS["warning"]
            else:
                bar_color = self.COLORS["danger"]

            if fill_width > 0:
                pygame.draw.rect(
                    self.screen, bar_color, (bar_x, bar_y, fill_width, bar_height), border_radius=9
                )

            # 百分比文字
            pct_text = self.font_small.render(f"{battery_pct:.0f}%", True, (255, 255, 255))
            text_rect = pct_text.get_rect(center=(bar_x + bar_width // 2, bar_y + bar_height // 2))
            self.screen.blit(pct_text, text_rect)

            y_offset += card_height + 8

    def draw_top_bar(self, context):
        """
        绘制顶部信息栏 - 现代化设计
        Args:
            context: 仿真上下文对象
        """
        # 绘制渐变背景
        header_height = 100
        for i in range(header_height):
            alpha = int(255 * (1 - i / header_height * 0.2))
            color = (52, 58, 64)
            pygame.draw.line(self.screen, color, (0, i), (self.window_width, i))

        # 标题
        title = self.font_large.render("Campus Fleet AI", True, self.COLORS["header_text"])
        self.screen.blit(title, (20, 20))

        # 副标题
        subtitle = self.font_small.render("Multi-Agent Delivery System", True, (200, 200, 200))
        self.screen.blit(subtitle, (20, 50))

        # 右侧信息卡片
        stats_x = self.window_width - 250

        # 策略信息
        strategy = context.scheduler.get_strategy_name()
        strategy_label = self.font_small.render("Strategy:", True, (180, 180, 180))
        strategy_text = self.font_small.render(strategy, True, self.COLORS["header_text"])
        self.screen.blit(strategy_label, (stats_x, 25))
        self.screen.blit(strategy_text, (stats_x + 70, 25))

        # 充电站信息
        stations = len(context.grid_env.charging_stations)
        station_label = self.font_small.render("Stations:", True, (180, 180, 180))
        station_text = self.font_small.render(f"{stations}", True, self.COLORS["warning"])
        self.screen.blit(station_label, (stats_x, 50))
        self.screen.blit(station_text, (stats_x + 70, 50))

        # 分隔线
        pygame.draw.line(
            self.screen,
            (80, 80, 80),
            (0, header_height - 1),
            (self.window_width, header_height - 1),
            2,
        )

    def render(self, context):
        """
        渲染整个界面
        Args:
            context: 仿真上下文对象
        """
        # 清屏
        self.screen.fill(self.COLORS["background"])

        # 绘制顶部信息栏
        self.draw_top_bar(context)

        # 绘制网格
        self.draw_grid(context.grid_env.grid, context.grid_env.charging_stations)

        # 绘制订单标记
        pending_orders = context.order_agent.get_pending_orders()
        self.draw_order_markers(pending_orders)

        # 绘制车辆
        for car in context.cars:
            self.draw_car(car.position, car.car_id, car.state.value, car.get_battery_percentage())

        # 绘制信息面板
        self.draw_info_panel(context)

        # 更新显示
        pygame.display.flip()
        self.clock.tick(self.fps)

    def close(self):
        """关闭Pygame窗口"""
        pygame.quit()
        sys.exit()
