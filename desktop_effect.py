# 参考资料：
#   - [Qt桌面粒子特效](https://github.com/Italink/DesktopParticlesEffect)实现
import sys, math, random
from plugin import *
from qfluentwidgets import (
    FluentIcon as FIF,
)

class TriangleEffectConfig:
    num = 100  # 点的个数
    pointSize = 6  # 点（圆）的大小
    maxLenOfLine = 100  # 两点的距离小于此值时连线
    lenOfRate = 2.5  # 点的运动速度范围（20ms移动多少）
    minRate = 0.5  # 点的最小运动速度
    # lineColor = QColor(85, 171, 228)  # 线的颜色
    lineColor = QColor(Qt.GlobalColor.blue)  # 线的颜色
    effectColor = QColor(0, 0, 255)  # 阴影的颜色
    lenOfLink = 20  # 鼠标移动时，目标位置与20ms前的位置的距离如果大于此值，则一个点移动到当前位置

class TrianglePoint:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y
        # 速度
        self.rate = TriangleEffectConfig.minRate + random.randint(0, int(TriangleEffectConfig.lenOfRate * 10)) / 10.0
        # 角度的x y分量
        self.angle = [math.cos(0), math.sin(0)]
        # 大小
        self.size = TriangleEffectConfig.pointSize

    def getY(self):
        return self.y

    def setY(self, value):
        self.y = round(value)

    def getX(self):
        return self.x

    def setX(self, value):
        self.x = round(value)

    def getRate(self):
        return self.rate

    def setRate(self, value):
        self.rate = value

    def run(self):
        self.x += self.rate * self.angle[0]
        self.y += self.rate * self.angle[1]

    def getDistance(self, other):
        '''计算两点间的距离'''
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def getRect(self):
        '''获取显示矩形，也就是点（圆）'''
        r = (TriangleEffectConfig.pointSize * self.rate - TriangleEffectConfig.minRate) / TriangleEffectConfig.lenOfRate
        return QRectF(self.x - r / 2, self.y - r / 2, r, r)

    def getAngle(self):
        return math.asin(self.angle[0])

    def setAngle(self, value):
        '''修改角度'''
        self.angle[0] = math.cos(value)
        self.angle[1] = math.sin(value)

    def reversalX(self):
        '''反转水平角度'''
        self.angle[0] *= -1
        self.randRate()

    def reversalY(self):
        '''反转垂直角度'''
        self.angle[1] *= -1
        self.randRate()

    def randRate(self):
        '''设置随机速度'''
        self.rate = TriangleEffectConfig.minRate + random.randint(0, int(TriangleEffectConfig.lenOfRate * 10)) / 10.0

    def getSize(self):
        return self.size

    def setSize(self, value):
        self.size = value

class AnimationThread(QThread):
    paintChange = pyqtSignal()
    def run(self):
        while True:
            self.msleep(42);
            self.paintChange.emit()

class TriangleEffectWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.updateTread = AnimationThread()
        self.updateTread.paintChange.connect(self.run)
        self.points = []
        self.lastPos = QPoint()

    def startEffectAnimation(self):
        self.__initRand()
        self.__initPoint(TriangleEffectConfig.num)

        # # 阴影效果，不能使用这个作为阴影，会出现报错
        # shadow = QGraphicsDropShadowEffect(self)
        # shadow.setOffset(0, 0)
        # c = QColor(Config.effectColor)
        # c = c.darker()
        # shadow.setColor(c)
        # shadow.setBlurRadius(20)
        # self.setGraphicsEffect(shadow)

        self.updateTread.start()

    def __initPoint(self, n):
        w = self.rect().width() / n
        h = self.rect().height() / 2

        for i in range(n):
            p = TrianglePoint(w * i, h)
            p.setAngle(random.randint(0, 360) * (math.pi / 180))
            p.randRate()
            self.points.append(p)

        self.points[0].setSize(0)

    def __initRand(self):
        random.seed(QTime(0,0,0).secsTo(QTime.currentTime()))

    def __collisionDetection(self):
        for point in self.points:
            # 处理每个点的移动和碰撞检测
            point.run()
            if point.getX() < 0 or point.getX() > self.rect().width():
                point.reversalX()
            if point.getY() < 0 or point.getY() > self.rect().height():
                point.reversalY()

    def run(self):
        self.__collisionDetection()

        self.points[0].setX(QCursor.pos().x())
        self.points[0].setY(QCursor.pos().y())

        for point in self.points[1:]:
            point.run()

        x = (self.lastPos.x() - QCursor.pos().x())
        y = (self.lastPos.y() - QCursor.pos().y())

        if (x * x + y * y)**0.5 > TriangleEffectConfig.lenOfLink:
            index = 1 + random.randint(0, len(self.points)-2)
            self.points[index].setX(self.lastPos.x())
            self.points[index].setY(self.lastPos.y())

        self.lastPos = QCursor.pos()
        self.update()

    def closeEvent(self, a0):
        self.updateTread.terminate()
        return super().closeEvent(a0)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        pen = QPen()
        pen.setWidthF(1.2)
        painter.setPen(pen)
        c = QColor(TriangleEffectConfig.lineColor)
        c = c.lighter()

        for i in range(len(self.points)):
            for j in range(i + 1, len(self.points)):
                if self.points[i].getDistance(self.points[j]) < TriangleEffectConfig.maxLenOfLine:
                    c.setAlpha(round(TriangleEffectConfig.maxLenOfLine - self.points[i].getDistance(self.points[j])))
                    pen.setBrush(c)
                    painter.setPen(pen)
                    painter.drawLine(round(self.points[i].getX()), round(self.points[i].getY()),
                                     round(self.points[j].getX()), round(self.points[j].getY()))
                    c.setAlpha(round((TriangleEffectConfig.maxLenOfLine - self.points[i].getDistance(self.points[j])) / 3))
                    painter.setBrush(c)
                    for k in range(j + 1, len(self.points)):
                        if (self.points[k].getDistance(self.points[i]) < TriangleEffectConfig.maxLenOfLine and
                                self.points[k].getDistance(self.points[j]) < TriangleEffectConfig.maxLenOfLine):
                            # 画三角形
                            triangle = [QPointF(self.points[i].getX(), self.points[i].getY()),
                                        QPointF(self.points[j].getX(), self.points[j].getY()),
                                        QPointF(self.points[k].getX(), self.points[k].getY())]
                            painter.drawPolygon(triangle)

            painter.setBrush(QColor(252, 251, 243))
            painter.setPen(Qt.NoPen)
            if i:  # 画点
                painter.drawEllipse(self.points[i].getRect())


class DesktopEffectWindow(TriangleEffectWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setWindowFlag(Qt.WindowType.WindowTransparentForInput, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        # self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)

        self.setGeometry(QApplication.primaryScreen().geometry())
        self.startEffectAnimation()


class DesktopEffect(PluginInterface):
    def __init__(self):
        super().__init__()
        self.effectWnd = None

    @property
    def previewImages(self) -> list:
        # folderPath = os.path.join(self.runtimePath, "preview")
        # images = glob.glob(f"{folderPath}/*.*", recursive=False)
        # return images
        return []

    @property
    def name(self):
        return "DesktopEffect"

    @property
    def displayName(self):
        return "桌面鼠标移动特效"

    @property
    def desc(self):
        return "添加桌面鼠标滑动特效"

    @property
    def author(self) -> str:
        return "yaoxuanzhi"

    @property
    def icon(self):
        # return QIcon(self.runtimePath + "/icons/ocr_process_display.svg")
        return FIF.RETURN

    @property
    def version(self) -> str:
        return "v1.0.0"

    @property
    def url(self) -> str:
        return "https://github.com/InterwovenCode/desktop_effect"

    @property
    def tags(self) -> list:
        return ["desktop","effect"]

    def onChangeEnabled(self):
        if self.enable:
            self.effectWnd = DesktopEffectWindow()
            self.effectWnd.show()
        else:
            self.effectWnd.close()
            self.effectWnd = None