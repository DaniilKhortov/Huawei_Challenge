import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, QLabel, QLineEdit, QHBoxLayout
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
        glTranslatef(-1.75, -0.5, -5)
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
        
        self.obj_file = "D:/KPI/huyavei/3D Manualy/result.obj"
        
        # Час останньої зміни файлу
        self.last_mod_time = os.path.getmtime(self.obj_file)
        self.opengl_widget.load_obj_file(self.obj_file)

        # Таймер перевірки змін файлу
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.check_for_updates)
        
        # Перевіряти щосекунди
        self.update_timer.start(1000)  
        
        # Ініціалізація й розміщення кнопок
        self.button = QPushButton('Input data', self)
        self.toggle_button = QPushButton('Toggle Render Mode', self)
        self.toggle_button.clicked.connect(self.opengl_widget.toggle_render_mode)  
        
        self.toggle_r_button = QPushButton('Toggle Rotate Mode', self)
        self.toggle_r_button.clicked.connect(self.opengl_widget.toggle_rotate_mode)  
        
        # Ініціалізація полей для вводу
        self.label_rho = QLabel("Густина, кг/м³:")
        self.input_rho = QLineEdit()
        self.label_cp = QLabel("Питома теплоємність, Дж/(кг·К):")
        self.input_cp = QLineEdit()
        self.label_k_thermal = QLabel("Теплопровідність, Вт/(м·К):")
        self.input_k_thermal = QLineEdit()
        self.label_mu = QLabel("Динамічна в'язкість, Па·с:")
        self.input_mu = QLineEdit()
        self.label_k_fluid = QLabel("Проникність рідини:")
        self.input_k_fluid = QLineEdit()        
        self.label_ne = QLabel("Кількість елементів:")
        self.input_ne = QLineEdit()
        self.label_x_lower = QLabel("Нижня межа по x :")
        self.input_x_lower = QLineEdit()
        self.label_x_upper = QLabel("Верхня межа по x :")
        self.input_x_upper = QLineEdit()
        
        # Віджети зліва
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.opengl_widget, stretch=4)
        left_layout.addWidget(self.toggle_button)
        left_layout.addWidget(self.toggle_r_button)
        
        # Віджети справа
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.label_rho)
        right_layout.addWidget(self.input_rho)
        right_layout.addWidget(self.label_cp)
        right_layout.addWidget(self.input_cp)
        right_layout.addWidget(self.label_k_thermal)
        right_layout.addWidget(self.input_k_thermal)
        right_layout.addWidget(self.label_mu)
        right_layout.addWidget(self.input_mu)
        right_layout.addWidget(self.label_k_fluid)
        right_layout.addWidget(self.input_k_fluid)
        right_layout.addWidget(self.label_ne)
        right_layout.addWidget(self.input_ne)
        right_layout.addWidget(self.label_x_lower)
        right_layout.addWidget(self.input_x_lower)
        right_layout.addWidget(self.label_x_upper)
        right_layout.addWidget(self.input_x_upper)
        right_layout.addWidget(self.button)
        
        # Об'єднання всіх віджетів у горизонтальний макет
        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout, stretch=2)
        main_layout.addLayout(right_layout, stretch=1)
        
        container = QWidget()
        container.setLayout(main_layout)
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