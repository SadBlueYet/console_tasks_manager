import sqlite3
from datetime import datetime
import threading
import time

class DataBase:
    def __init__(self, title):
        self.title = title
        self.con = sqlite3.connect(f"{title}.db") #connecting to database
        self.cur = self.con.cursor()

   
    def create_database(self): #Creating to database
        self.cur.execute(f"CREATE TABLE IF NOT EXISTS {self.title} ( id INTEGER PRIMARY KEY AUTOINCREMENT,"
                         " task_name TEXT, task_definition TEXT, priority INTEGER, reminder_date TEXT, execution_status TEXT)")
    

    def create_task(self, task_name, task_definition, priority, reminder_date, execution_status):

        query = f"INSERT INTO {self.title} (task_name, task_definition, priority, reminder_date, execution_status) VALUES (?, ?, ?, ?, ?)"
        values = (task_name, task_definition, priority, reminder_date, execution_status)

        try:
            self.cur.execute(query, values)
            self.con.commit()
            print("Задача успешно добавлена")
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении задачи: {e}")
        
    def changing_the_task(self, column_name_changing, change, task_name):
        query = f"""UPDATE {self.title} SET {column_name_changing} = ? WHERE task_name = ?"""
        values = (change, task_name)

        try:
            self.cur.execute(query, values)
            self.con.commit()
            print("Задача успешно обновлена!")
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении задачи: {e}")

    def get_task(self, task_name):
        query = f"SELECT * FROM {self.title} WHERE task_name = ?"

        try:
            self.cur.execute(query, (task_name,))
            task = self.cur.fetchone()
            print('ID:', task[0])
            print('Название:', task[1])
            print('Описание:', task[2])
            print('Приоритет:', task[3])
            print('Дата напоминания:', task[4])
            print('Статус выполнения:', task[5], '\n\n')
        except sqlite3.Error as e:
            print(f"Ошибка при получении задачи: {e}")

    def get_all_tasks(self): #Getting a list of all tasks
        query = f"SELECT * FROM {self.title}"
        try:
            self.cur.execute(query)
            tasks = self.cur.fetchall()
            return tasks

        except sqlite3.Error as e:
            print(f"Ошибка при получении задач: {e}") 

    def get_tasks_sorted_by_priority(self):#Getting sorted tasks by priority
        query = f"SELECT * FROM {self.title} ORDER BY priority ASC" 
        try:
            self.cur.execute(query)
            sorted_tasks = self.cur.fetchall()
            return sorted_tasks
        except sqlite3.Error as e:
            print(f"Ошибка при получении отсортированных задач: {e}")
            return []
       
    def print_task(self, tasks):
        for task in tasks:
            print('ID:', task[0])
            print('Название:', task[1])
            print('Описание:', task[2])
            print('Приоритет:', task[3])
            print('Дата напоминания:', task[4])
            print('Статус выполнения:', task[5], '\n\n')

def get_tasks_to_remind(title):
        user_tasks = DataBase(title)

        while True:
            time.sleep(60)
            current_time = datetime.now()
            query = f"SELECT * FROM {title} WHERE reminder_date <= ?"
            values = (current_time.strftime("%d.%m.%Y %H:%M"),)

            try:
                user_tasks.cur.execute(query, values)
                tasks_to_remind = user_tasks.cur.fetchall()

                for task in tasks_to_remind:
                    query = f"""UPDATE {title} SET reminder_date = NULL WHERE reminder_date = ?"""
                    values = (task[4],) 
                    user_tasks.cur.execute(query, values)
                    user_tasks.con.commit()
                    print('ID:', task[0])
                    print('Название:', task[1])
                    print('Описание:', task[2])
                    print('Приоритет:', task[3])
                    print('Дата напоминания:', task[4])
                    print('Статус выполнения:', task[5], '\n\n')

            except sqlite3.Error as e:
                print(f"Ошибка при получении задач для напоминания: {e}")



if __name__ == '__main__':
    
    print('Здравствуйте! Вас приветствует менеджер задач!\n\n')
    title = input("Введите название таблицы задач:")

    user_tasks = DataBase(title)
    user_tasks.create_database()

    #Creating and launching a reminder thread
    thread = threading.Thread(target=get_tasks_to_remind, args=(title,)) 
    thread.start()
    
    while 1:
        user_choise = int(input('1 - Добавить задачу\n'
                            '2 - Редактировать задачу\n'
                            '3 - Показать задачу\n'
                            '4 - Показать все задачи\n'
                            '5 - Показать отсортированные задачи(по приоритету)\n>>'))
        match user_choise:
            case 1:
                task_name = input('Введите название задачи\n>>')
                task_definition = input('Введите описание задачи\n>>')
                task_priority = input('Введите приоритет задачи (от 1 до 10)\n>>')
                reminder_date = input('Введите дату и время напоминания (ДД.ММ.ГГГГ ЧЧ:ММ) \n>>')
                execution_status = input('Введите статус выполнения задачи\n>>')
                
                user_tasks.create_task(task_name, task_definition, task_priority, reminder_date, execution_status)
            
            case 2:
                task_name = input("Ввдите название задачи\n>>")
                column_name_changing = int(input('Что вы хотите изменить?\n'
                                             '1 - Название\n2- Описание\n3 - Приоритет\n'
                                             '4 - Время\n5 - Статус\n>>'))
                
                match column_name_changing:
                    case 1:
                        column_name_changing = 'task_name'
                    case 2:
                        column_name_changing = 'task_definition'
                    case 3:
                        column_name_changing = 'priority'
                    case 4:
                        column_name_changing = 'reminder_date'
                    case 5:
                        column_name_changing = 'execution_status'

                change = input("Введите изменение\n>>") 
                user_tasks.changing_the_task(column_name_changing, change, task_name)

            case 3:
                task_name = input('Введите название задачи\n>>')
                user_tasks.get_task(task_name)
            case 4:
                user_tasks.print_task(user_tasks.get_all_tasks())
            case 5:
                user_tasks.print_task(user_tasks.get_tasks_sorted_by_priority())
