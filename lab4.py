import os
import csv
import datetime
from typing import List, Union, Iterator, Optional

class MedicalRecord:
    """Базовый класс для представления медицинской записи"""
    __slots__ = ('_id', '_patient_name', '_doctor_name', '_reason', '_duration', '_date')
    
    def __init__(self, 
                 id: int, 
                 patient_name: str, 
                 doctor_name: str, 
                 reason: str, 
                 duration: int, 
                 date: str = None):
        # Установка значений через setattr
        setattr(self, '_id', id)
        setattr(self, '_patient_name', patient_name)
        setattr(self, '_doctor_name', doctor_name)
        setattr(self, '_reason', reason)
        setattr(self, '_duration', duration)
        setattr(self, '_date', date or datetime.date.today().isoformat())
    
    # Свойства для доступа к атрибутам
    @property
    def id(self) -> int:
        return self._id
    
    @property
    def patient_name(self) -> str:
        return self._patient_name
    
    @property
    def doctor_name(self) -> str:
        return self._doctor_name
    
    @property
    def reason(self) -> str:
        return self._reason
    
    @property
    def duration(self) -> int:
        return self._duration
    
    @property
    def date(self) -> str:
        return self._date
    
    def __repr__(self) -> str:
        """Перегрузка repr() для вывода информации об объекте"""
        return (f"MedicalRecord(id={self.id}, patient='{self.patient_name}', "
                f"doctor='{self.doctor_name}', reason='{self.reason}', "
                f"duration={self.duration}, date='{self.date}')")
    
    def __str__(self) -> str:
        """Перегрузка str() для удобного вывода"""
        return f"{self.id:3} | {self.patient_name:20} | {self.doctor_name:15} | {self.reason:20} | {self.duration:4} мин | {self.date}"

class EmergencyRecord(MedicalRecord):
    """Класс для экстренных медицинских записей (наследуется от MedicalRecord)"""
    __slots__ = ('_urgency',)
    
    URGENCY_LEVELS = {1: "критическая", 2: "высокая", 3: "средняя"}
    
    def __init__(self, 
                 id: int, 
                 patient_name: str, 
                 doctor_name: str, 
                 reason: str, 
                 duration: int, 
                 urgency: int,
                 date: str = None):
        super().__init__(id, patient_name, doctor_name, reason, duration, date)
        setattr(self, '_urgency', urgency)
    
    @property
    def urgency(self) -> int:
        return self._urgency
    
    def __repr__(self) -> str:
        """Перегрузка repr() с учетом срочности"""
        return (f"EmergencyRecord(id={self.id}, patient='{self.patient_name}', "
                f"doctor='{self.doctor_name}', reason='{self.reason}', "
                f"duration={self.duration}, urgency={self.urgency}, date='{self.date}')")
    
    def __str__(self) -> str:
        """Перегрузка str() с указанием срочности"""
        urgency_str = self.URGENCY_LEVELS.get(self.urgency, "неизвестная")
        return f"{super().__str__()} | Срочность: {urgency_str}"

class MedicalRecordsCollection:
    """Коллекция медицинских записей с возможностью итерации и доступа по индексу"""
    def __init__(self):
        self._records = []
    
    def __iter__(self) -> Iterator[Union[MedicalRecord, EmergencyRecord]]:
        """Реализация итератора"""
        return iter(self._records)
    
    def __getitem__(self, index: int) -> Union[MedicalRecord, EmergencyRecord]:
        """Доступ к элементам по индексу"""
        return self._records[index]
    
    def __len__(self) -> int:
        return len(self._records)
    
    def __repr__(self) -> str:
        return f"MedicalRecordsCollection({len(self)} records)"
    
    def add(self, record: Union[MedicalRecord, EmergencyRecord]):
        """Добавление записи в коллекцию"""
        self._records.append(record)
    
    def sort_by_patient_name(self) -> 'MedicalRecordsCollection':
        """Сортировка по имени пациента"""
        sorted_collection = MedicalRecordsCollection()
        sorted_collection._records = sorted(self._records, key=lambda r: r.patient_name)
        return sorted_collection
    
    def sort_by_duration(self) -> 'MedicalRecordsCollection':
        """Сортировка по длительности приема"""
        sorted_collection = MedicalRecordsCollection()
        sorted_collection._records = sorted(self._records, key=lambda r: r.duration)
        return sorted_collection
    
    def filter_by_duration(self, min_duration: int) -> 'MedicalRecordsCollection':
        """Фильтрация по минимальной длительности"""
        filtered_collection = MedicalRecordsCollection()
        filtered_collection._records = [r for r in self._records if r.duration > min_duration]
        return filtered_collection
    
    def get_emergency_records(self) -> Iterator[EmergencyRecord]:
        """Генератор для получения экстренных записей"""
        for record in self._records:
            if isinstance(record, EmergencyRecord):
                yield record
    
    def get_records_by_doctor(self, doctor_name: str) -> Iterator[MedicalRecord]:
        """Генератор для получения записей по врачу"""
        for record in self._records:
            if record.doctor_name == doctor_name:
                yield record
    
    @staticmethod
    def load_from_csv(filename: str) -> 'MedicalRecordsCollection':
        """Статический метод для загрузки данных из CSV-файла"""
        collection = MedicalRecordsCollection()
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Преобразование типов
                    id = int(row['id'])
                    duration = int(row['duration'])
                    urgency = int(row.get('urgency', 0))
                    
                    # Создание соответствующего типа записи
                    if urgency > 0:
                        record = EmergencyRecord(
                            id=id,
                            patient_name=row['patient_name'],
                            doctor_name=row['doctor_name'],
                            reason=row['reason'],
                            duration=duration,
                            urgency=urgency,
                            date=row.get('date')
                        )
                    else:
                        record = MedicalRecord(
                            id=id,
                            patient_name=row['patient_name'],
                            doctor_name=row['doctor_name'],
                            reason=row['reason'],
                            duration=duration,
                            date=row.get('date')
                        )
                    collection.add(record)
            print(f"Загружено {len(collection)} записей из {filename}")
        except FileNotFoundError:
            print(f"Файл {filename} не найден. Будет создан новый.")
        except Exception as e:
            print(f"Ошибка при загрузке файла: {e}")
        return collection
    
    @staticmethod
    def save_to_csv(collection: 'MedicalRecordsCollection', filename: str):
        """Статический метод для сохранения данных в CSV-файл"""
        if not collection:
            print("Нет данных для сохранения!")
            return
        
        fieldnames = ['id', 'patient_name', 'doctor_name', 'reason', 'duration', 'date', 'urgency']
        
        try:
            with open(filename, 'w', encoding='utf-8', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                
                for record in collection:
                    row = {
                        'id': record.id,
                        'patient_name': record.patient_name,
                        'doctor_name': record.doctor_name,
                        'reason': record.reason,
                        'duration': record.duration,
                        'date': record.date,
                        'urgency': getattr(record, 'urgency', 0)
                    }
                    writer.writerow(row)
            print(f"Сохранено {len(collection)} записей в {filename}")
        except Exception as e:
            print(f"Ошибка при сохранении файла: {e}")
    
    def print_all(self):
        """Вывод всех записей в удобочитаемом формате"""
        if not self._records:
            print("Нет данных для отображения")
            return
        
        print("\n" + "=" * 120)
        print(f"{'ID':3} | {'Пациент':20} | {'Врач':15} | {'Причина':20} | {'Длит.':5} | {'Дата':10} | {'Срочность':10}")
        print("=" * 120)
        for record in self._records:
            print(record)
        print("=" * 120)

def count_files_in_directory(path: str = ".") -> int:
    """Подсчет количества файлов в директории"""
    try:
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        print(f"Количество файлов в директории '{path}': {len(files)}")
        return len(files)
    except FileNotFoundError:
        print(f"Директория '{path}' не найдена!")
        return 0

def main():
    """Основная функция программы"""
    # 1. Подсчет файлов в текущей директории
    count_files_in_directory()
    
    # 2. Загрузка данных
    collection = MedicalRecordsCollection.load_from_csv("data.csv")
    
    while True:
        print("\n" + "=" * 50)
        print(" Система учета посещений поликлиники")
        print("=" * 50)
        print("1. Показать все записи")
        print("2. Сортировать по ФИО пациента")
        print("3. Сортировать по длительности приема")
        print("4. Фильтровать по длительности (> N минут)")
        print("5. Показать экстренные случаи")
        print("6. Добавить новую запись")
        print("7. Сохранить данные")
        print("8. Показать записи по врачу (генератор)")
        print("0. Выход")
        
        choice = input("Выберите действие: ")
        
        if choice == '1':
            collection.print_all()
        
        elif choice == '2':
            sorted_collection = collection.sort_by_patient_name()
            sorted_collection.print_all()
        
        elif choice == '3':
            sorted_collection = collection.sort_by_duration()
            sorted_collection.print_all()
        
        elif choice == '4':
            try:
                min_duration = int(input("Введите минимальную длительность (мин): "))
                filtered = collection.filter_by_duration(min_duration)
                filtered.print_all()
            except ValueError:
                print("Ошибка ввода! Введите число.")
        
        elif choice == '5':
            print("\nЭкстренные случаи:")
            for emergency in collection.get_emergency_records():
                print(emergency)
        
        elif choice == '6':
            try:
                id = max(r.id for r in collection) + 1 if collection else 1
                patient = input("ФИО пациента: ")
                doctor = input("ФИО врача: ")
                reason = input("Причина обращения: ")
                duration = int(input("Длительность (мин): "))
                
                # Спросим, экстренный ли случай
                if input("Экстренный случай? (y/n): ").lower() == 'y':
                    urgency = int(input("Уровень срочности (1-крит., 2-выс., 3-сред.): "))
                    record = EmergencyRecord(id, patient, doctor, reason, duration, urgency)
                else:
                    record = MedicalRecord(id, patient, doctor, reason, duration)
                
                collection.add(record)
                print("Запись успешно добавлена!")
            
            except ValueError:
                print("Ошибка ввода данных!")
        
        elif choice == '7':
            MedicalRecordsCollection.save_to_csv(collection, "data.csv")
        
        elif choice == '8':
            doctor = input("Введите ФИО врача: ")
            print(f"\nЗаписи врача {doctor}:")
            for record in collection.get_records_by_doctor(doctor):
                print(record)
        
        elif choice == '0':
            if input("Сохранить изменения перед выходом? (y/n): ").lower() == 'y':
                MedicalRecordsCollection.save_to_csv(collection, "data.csv")
            print("Выход из программы")
            break
        
        else:
            print("Неверный ввод!")

if __name__ == "__main__":
    main()