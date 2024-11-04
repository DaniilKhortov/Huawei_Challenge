import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, QLabel, QLineEdit
from PyQt5.QtCore import QTimer, Qt
from OpenGL.arrays import vbo 
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
        self.rotate_mode = 0  
        # self.x_translate = 0
        # self.y_translate = 0
        self.vbo = None  
        self.setup_vbo = False  
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
        glTranslatef(-1.25, -0.5, -5)
        self.timer.timeout.connect(self.updateGL)
        
    def setup_vertex_buffer_object(self):
        vertices = np.array([self.vertices[vertex] for face in self.faces for vertex in face], dtype=np.float32)
        self.vbo = vbo.VBO(vertices)  # Створіть VBO з numpy-масиву
        self.setup_vbo = False    
    #Відображення моделі 
    #Тут також реалізуються переміщення
    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        if self.setup_vbo:
            self.setup_vertex_buffer_object()
        self.vbo.bind()
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointerf(self.vbo)
        
        #####################!Маштаб
        glPushMatrix()
        glScalef(1.5, 1.5, 1.5)  
        if self.render_mode == 0:
            glDrawArrays(GL_QUADS, 0, len(self.faces) * 3)
        elif self.render_mode == 1:
            glDrawArrays(GL_TRIANGLES, 0, len(self.faces) * 3)            
        elif self.render_mode == 2:
            glDrawArrays(GL_QUAD_STRIP, 0, len(self.faces) * 3)
        glPopMatrix()
        #####################!Маштаб

        
        glDisableClientState(GL_VERTEX_ARRAY)
        self.vbo.unbind()
        
        
    #Зчитування стрілок з клавіш для руху моделі
#####################!Рухає по фокусу. Тобто рухається відносно сторони, на яку дивиться переднє ребро моделі
     
    # def keyPressEvent(self, event):
    #     if event.key() == Qt.Key_Left:
    #         self.x_translate -= 0.1
    #     elif event.key() == Qt.Key_Right:
    #         self.x_translate += 0.1
    #     elif event.key() == Qt.Key_Up:
    #         self.y_translate += 0.1
    #     elif event.key() == Qt.Key_Down:
    #         self.y_translate -= 0.1
    #     self.update()
        
    #Налаштування й атрибути режиму відображення
    # def draw_model(self):
    #     #Модель без контурів 
    #     if self.render_mode == 0: 
    #         glBegin(GL_TRIANGLES)
    #         for face in self.faces:
    #             for vertex in face:
    #                 glColor3fv([0.8, 0.3, 0.3]) 
    #                 glVertex3fv(self.vertices[vertex])
    #         glEnd()
    #     #Модель з контурами й заливкою     
    #     elif self.render_mode == 1:  
    #         glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    #         glBegin(GL_TRIANGLES)
    #         for face in self.faces:
    #             for vertex in face:
    #                 glColor3fv([0.8, 0.3, 0.3])  
    #                 glVertex3fv(self.vertices[vertex])
    #         glEnd()
            
            
    #         glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    #         glEnable(GL_POLYGON_OFFSET_LINE)
    #         glPolygonOffset(-1, -1)
    #         glColor3f(0, 0, 0)  
    #         glLineWidth(1.5)
    #         glBegin(GL_TRIANGLES)
    #         for face in self.faces:
    #             for vertex in face:
    #                 glVertex3fv(self.vertices[vertex])
    #         glEnd()
    #         glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)  
    #         glDisable(GL_POLYGON_OFFSET_LINE)
       
        # #Модель тільки з контурами          
        # elif self.render_mode == 2:    
        #           # Заповнення моделі червоним кольором
        #     glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)  
        #     glBegin(GL_TRIANGLES)
        #     for face in self.faces:
        #         for vertex in face:
        #             glColor3fv([0.8, 0.3, 0.3])  
        #             glVertex3fv(self.vertices[vertex])
        #     glEnd()
        #     glPolygonMode(GL_FRONT_AND_BACK, GL_FILL) 
             
       
    # Обертання моделі 
    def updateGL(self):
        
        if self.rotate_mode==0:  
            glRotatef(0.1, 1, 0, 0)  
        elif self.rotate_mode==1:  
            glRotatef(0.1, 0, 1, 0)  
        elif self.rotate_mode==2:  
            glRotatef(0.1, 0, 0, 1)            
        elif self.rotate_mode==3:  
            glRotatef(0.1, 0, 0, 0) 
                          
        self.update()  
        
    # Зміна режиму відображення для  paintGL
    def toggle_render_mode(self):
        self.render_mode = (self.render_mode + 1) % 3  
        self.update() 
         
    # Зміна режиму обертання 
    def toggle_rotate_mode(self):
        self.rotate_mode = (self.rotate_mode + 1) % 4  
        self.update() 
                    
    # Завантаження файлу .obj
    def load_obj_file(self, filename):
        self.vertices, self.faces = load_obj(filename)  
        self.setup_vbo = True  # Позначте, що потрібно створити VBO 
        
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
        
        self.toggle_r_button = QPushButton('Toggle Rotate Mode', self)
        self.toggle_r_button.clicked.connect(self.opengl_widget.toggle_rotate_mode)  
                
        rho = 1000 # густина, кг/м³ (для води)
        cp = 4184  # питома теплоємність, Дж/(кг·К)
        k_thermal = 0.6  # теплопровідність, Вт/(м·К)
        mu = 0.001  # динамічна в'язкість, Па·с
        k_fluid = 1e-12  # проникність рідини (для Дарсі)

        # Параметри сітки і області
        ne = 200  # кількість елементів (простий приклад)
        x_lower, x_upper = 0, 1  # межі по x        
                
                
        # Ініціалізація полей для вводу
        self.label_rho = QLabel("X Position:")
        self.input_rho = QLineEdit()
        self.label_cp = QLabel("Y Position:")
        self.input_cp = QLineEdit()
        self.label_k_thermal = QLabel("Z Position:")
        self.input_k_thermal = QLineEdit()
        self.mu = QLabel("Z Position:")
        self.mu = QLineEdit()
        self.k_fluid = QLabel("Z Position:")
        self.k_fluid = QLineEdit()        
        self.ne = QLabel("Z Position:")
        self.ne = QLineEdit()
        self.x_lower = QLabel("Z Position:")
        self.x_lower = QLineEdit()
        self.x_upper = QLabel("Z Position:")
        self.x_upper = QLineEdit()
        
        #Розміщення віджетів
        layout = QVBoxLayout()
        layout.addWidget(self.opengl_widget, stretch=4)
        
        
        layout.addWidget(self.opengl_widget)
        layout.addWidget(self.toggle_button) 
        layout.addWidget(self.toggle_r_button)  
        layout.addWidget(self.label_x)
        layout.addWidget(self.input_x)
        layout.addWidget(self.label_y)
        layout.addWidget(self.input_y)
        layout.addWidget(self.label_z)
        layout.addWidget(self.input_z)
        layout.addWidget(self.button)

        
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