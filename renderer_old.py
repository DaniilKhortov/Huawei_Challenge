import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, QLabel, QLineEdit
from PyQt5.QtCore import QTimer, Qt

from PyQt5.QtOpenGL import QGLWidget
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import os
import sys

#Функція зчитування .obj файлів
def load_obj(filename):
    vertices = []
    faces = []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('v '):
                # Беремо тільки перші три компоненти
                vertex = list(map(float, line.strip().split()[1:4]))
                vertices.append(vertex)
            elif line.startswith('f '):
                face = [int(val.split('/')[0]) - 1 for val in line.strip().split()[1:]]
                faces.append(face)
    return np.array(vertices, dtype=np.float32), np.array(faces, dtype=np.int32)


#Вивід 3Д моделі як віджет для інтерфейсу 
#Тут атрибути відображення
class OpenGLWidget(QGLWidget):
    #Конструктор. Ініціалізація віджету й змінних
    def __init__(self, parent=None):
        super(OpenGLWidget, self).__init__(parent)
        self.vertices = None
        self.faces = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateGL)
        self.timer.start(16)  
        self.render_mode = 0  
        self.x_translate = 0
        self.y_translate = 0
        
        self.setFocusPolicy(Qt.StrongFocus)  
        
    #Ініціалізація сцени OpenGL   
    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glLightfv(GL_LIGHT0, GL_POSITION, [1, 1, 1, 0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glEnable(GL_LIGHT1)
        glLightfv(GL_LIGHT1, GL_POSITION, [-1, -1, -1, 0])
        glLightfv(GL_LIGHT1, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        glLightfv(GL_LIGHT1, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.5, 0.5, 0.5, 1.0])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glMaterialf(GL_FRONT, GL_SHININESS, 50)
        glMatrixMode(GL_PROJECTION)
        gluPerspective(45, 1.33, 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)
        glTranslatef(-0.5, -0.5, -5)
        
    #Відображення моделі 
    #Тут також реалізуються переміщення
    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        glTranslatef(self.x_translate, self.y_translate, 0)  
        if self.vertices is not None and self.faces is not None:
            self.draw_model()
        glPopMatrix()
        
    #Зчитування стрілок з клавіш для руху моделі
#####################!Рухає по фокусу. Тобто рухається відносно сторони, на яку дивиться переднє ребро моделі
     
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            self.x_translate -= 0.1
        elif event.key() == Qt.Key_Right:
            self.x_translate += 0.1
        elif event.key() == Qt.Key_Up:
            self.y_translate += 0.1
        elif event.key() == Qt.Key_Down:
            self.y_translate -= 0.1
        self.update()
        
    #Налаштування й атрибути режиму відображення
    def draw_model(self):
        #Модель без контурів 
        if self.render_mode == 0: 
            glBegin(GL_TRIANGLES)
            for face in self.faces:
                for vertex in face:
                    glColor3fv([0.8, 0.3, 0.3]) 
                    glVertex3fv(self.vertices[vertex])
            glEnd()
        #Модель з контурами й заливкою     
        elif self.render_mode == 1:  
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            glBegin(GL_TRIANGLES)
            for face in self.faces:
                for vertex in face:
                    glColor3fv([0.8, 0.3, 0.3])  
                    glVertex3fv(self.vertices[vertex])
            glEnd()
            
            
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            glEnable(GL_POLYGON_OFFSET_LINE)
            glPolygonOffset(-1, -1)
            glColor3f(0, 0, 0)  
            glLineWidth(1.5)
            glBegin(GL_TRIANGLES)
            for face in self.faces:
                for vertex in face:
                    glVertex3fv(self.vertices[vertex])
            glEnd()
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)  
            glDisable(GL_POLYGON_OFFSET_LINE)
       
        #Модель тільки з контурами          
        elif self.render_mode == 2:    
                  # Заповнення моделі червоним кольором
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)  
            glBegin(GL_TRIANGLES)
            for face in self.faces:
                for vertex in face:
                    glColor3fv([0.8, 0.3, 0.3])  
                    glVertex3fv(self.vertices[vertex])
            glEnd()
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL) 
             
       
    # Обертання моделі 
    def updateGL(self):
        glRotatef(1, 3, 1, 1)  
        self.update()  
        
    # Зміна режиму відображення для  draw_model
    def toggle_render_mode(self):
        self.render_mode = (self.render_mode + 1) % 3  
        self.update()  
            
    # Завантаження файлу .obj
    def load_obj_file(self, filename):
        self.vertices, self.faces = load_obj(filename)  
          
# Інтерфейс користувача       
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        # Налаштування вікна
        self.setWindowTitle('Radiator modelling 3D')
        self.setGeometry(100, 100, 1400, 1000)
        
        # виклик віджета
        self.opengl_widget = OpenGLWidget(self)
        
############################################################################################ шлях до файлу .obj
        self.obj_file = "D:/KPI/huyavei/3D Manualy/result.obj"  
        
        # Час останньої зміни файлу
        self.last_mod_time = os.path.getmtime(self.obj_file)
        self.opengl_widget.load_obj_file(self.obj_file)

        #Таймер  перевірки змін файлу
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.check_for_updates)
        
        #Перевіряти щосекунди
        self.update_timer.start(1000)  
        
        # Ініціалізація й розміщення кнопок
        self.button = QPushButton('Input data', self)
        self.toggle_button = QPushButton('Toggle Render Mode', self)
        self.toggle_button.clicked.connect(self.opengl_widget.toggle_render_mode)  
        
        # Ініціалізація полей для вводу
        self.label_x = QLabel("X Position:")
        self.input_x = QLineEdit()
        self.label_y = QLabel("Y Position:")
        self.input_y = QLineEdit()
        self.label_z = QLabel("Z Position:")
        self.input_z = QLineEdit()
        
        
        #Розміщення віджетів
        layout = QVBoxLayout()
        layout.addWidget(self.opengl_widget, stretch=4)
        
        
        layout.addWidget(self.opengl_widget)
        
        layout.addWidget(self.label_x)
        layout.addWidget(self.input_x)
        layout.addWidget(self.label_y)
        layout.addWidget(self.input_y)
        layout.addWidget(self.label_z)
        layout.addWidget(self.input_z)
        layout.addWidget(self.button)
        layout.addWidget(self.toggle_button)  
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        
    # Функція перевірки наявності змін у файлі
    def check_for_updates(self):

        current_mod_time = os.path.getmtime(self.obj_file)
        if current_mod_time != self.last_mod_time:
            self.last_mod_time = current_mod_time
            self.opengl_widget.load_obj_file(self.obj_file)
            print("Модель оновлена")
        
    #####################################################################################Функція відкриття файлів    
    # def open_file_dialog(self):
    #     options = QFileDialog.Options()
    #     fileName, _ = QFileDialog.getOpenFileName(self, "Open OBJ File", "", "OBJ Files (*.obj);;All Files (*)", options=options)
    #     if fileName:
    #         self.opengl_widget.load_obj_file(fileName)   
  

# Виклик додатку з інтерфейсом          
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    
    window.show()
    
    sys.exit(app.exec_())                 