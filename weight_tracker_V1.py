#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Viktspårnings App
En modern app för att spåra viktförändringar med grafer och analyser
"""

import sys
import json
import os
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTableWidget, QTableWidgetItem, QTabWidget,
                             QMessageBox, QDateEdit, QGroupBox, QFormLayout,
                             QHeaderView, QSpinBox, QDoubleSpinBox, QCheckBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np


def exponential_smoothing(data, alpha=0.3):
    """
    Exponentiell utjämning för viktdata
    Alpha: 0-1, högre värde = mer vikt på senaste data
    """
    if len(data) < 2:
        return data
    
    smoothed = [data[0]]
    for i in range(1, len(data)):
        smoothed.append(alpha * data[i] + (1 - alpha) * smoothed[i-1])
    return smoothed


def weighted_moving_average(weights, window=7):
    """
    Viktad glidande medelvärde - ger mer vikt åt senaste mätningar
    """
    if len(weights) < window:
        window = len(weights)
    
    wma = []
    for i in range(len(weights)):
        if i < window - 1:
            # För få datapunkter, använd vad vi har
            subset = weights[:i+1]
            # Skapa vikter: senaste får högst vikt
            w = np.arange(1, len(subset) + 1)
        else:
            subset = weights[i-window+1:i+1]
            w = np.arange(1, window + 1)
        
        # Normalisera vikter
        w = w / w.sum()
        wma.append(np.dot(subset, w))
    
    return wma


def predict_weight_improved(dates, weights, target_weight, method='exponential'):
    """
    Förbättrad viktprediktion med flera metoder
    
    Metoder:
    - 'linear': Enkel linjär regression (snabbast, minst exakt)
    - 'exponential': Exponentiell utjämning (bra för kortsiktig)
    - 'weighted': Viktad MA (balanserad)
    - 'hybrid': Kombinerar flera metoder (bäst)
    """
    if len(dates) < 2:
        return None, None, None
    
    current_weight = weights[-1]
    current_date = dates[-1]
    
    # Konvertera datum till dagar
    x_numeric = np.array([(d - dates[0]).days for d in dates])
    y_weights = np.array(weights)
    
    # Metod 1: Linjär regression (baseline)
    z_linear = np.polyfit(x_numeric, y_weights, 1)
    weekly_change_linear = z_linear[0] * 7
    
    # Metod 2: Exponentiell utjämning (ger mer vikt åt senaste data)
    smoothed_exp = exponential_smoothing(weights, alpha=0.3)
    # Beräkna trend från exponentiell utjämning
    if len(smoothed_exp) > 10:
        recent_smooth = smoothed_exp[-10:]
        recent_x = x_numeric[-10:]
        z_exp = np.polyfit(recent_x, recent_smooth, 1)
        weekly_change_exp = z_exp[0] * 7
    else:
        weekly_change_exp = weekly_change_linear
    
    # Metod 3: Viktad MA
    wma = weighted_moving_average(weights, window=min(14, len(weights)))
    if len(wma) > 7:
        recent_wma = wma[-7:]
        recent_x_wma = x_numeric[-7:]
        z_wma = np.polyfit(recent_x_wma, recent_wma, 1)
        weekly_change_wma = z_wma[0] * 7
    else:
        weekly_change_wma = weekly_change_linear
    
    # Hybrid: Använd genomsnitt av metoderna, men ge mer vikt åt nyare metoder
    if method == 'hybrid':
        # Exponentiell och WMA viktigare än linjär
        weekly_change = (weekly_change_linear * 0.2 + 
                        weekly_change_exp * 0.4 + 
                        weekly_change_wma * 0.4)
    elif method == 'exponential':
        weekly_change = weekly_change_exp
    elif method == 'weighted':
        weekly_change = weekly_change_wma
    else:
        weekly_change = weekly_change_linear
    
    # Beräkna tid till mål
    if weekly_change >= 0 or current_weight <= target_weight:
        return None, None, None
    
    weight_to_lose = current_weight - target_weight
    weeks_to_goal = abs(weight_to_lose / weekly_change)
    projected_date = current_date + timedelta(weeks=weeks_to_goal)
    
    return weekly_change, weeks_to_goal, projected_date


class WeightData:
    """Klass för att hantera viktdata"""
    
    def __init__(self, filename='weight_data.json'):
        self.filename = filename
        self.data = self.load_data()
    
    def load_data(self):
        """Laddar data från JSON-fil"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Se till att visualization_settings finns
                    if 'visualization_settings' not in data:
                        data['visualization_settings'] = self.get_default_vis_settings()
                    return data
            except:
                return {'entries': [], 'profile': {}, 'visualization_settings': self.get_default_vis_settings()}
        return {'entries': [], 'profile': {}, 'visualization_settings': self.get_default_vis_settings()}
    
    def get_default_vis_settings(self):
        """Returnerar standardinställningar för visualisering"""
        return {
            'highlight_weekends': True,
            'highlight_days': [],  # Lista av veckodagar (0=Måndag, 6=Söndag)
            'show_events': True,
            'custom_events': []  # [{'date': 'YYYY-MM-DD', 'label': 'Text', 'color': '#hex'}]
        }
    
    def save_data(self):
        """Sparar data till JSON-fil"""
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def add_entry(self, date, weight, notes=''):
        """Lägger till en viktmätning"""
        entry = {
            'date': date,
            'weight': weight,
            'notes': notes
        }
        # Ta bort tidigare inmatning samma dag
        self.data['entries'] = [e for e in self.data['entries'] if e['date'] != date]
        self.data['entries'].append(entry)
        self.data['entries'].sort(key=lambda x: x['date'])
        self.save_data()
    
    def delete_entry(self, date):
        """Tar bort en viktmätning"""
        self.data['entries'] = [e for e in self.data['entries'] if e['date'] != date]
        self.save_data()
    
    def get_entries(self):
        """Returnerar alla mätningar"""
        return self.data['entries']
    
    def set_profile(self, height, target_weight, start_weight):
        """Sparar profildata"""
        self.data['profile'] = {
            'height': height,
            'target_weight': target_weight,
            'start_weight': start_weight
        }
        self.save_data()
    
    def get_profile(self):
        """Returnerar profildata"""
        return self.data['profile']
    
    def get_vis_settings(self):
        """Returnerar visualiseringsinställningar"""
        if 'visualization_settings' not in self.data:
            self.data['visualization_settings'] = self.get_default_vis_settings()
        return self.data['visualization_settings']
    
    def set_vis_settings(self, settings):
        """Sparar visualiseringsinställningar"""
        self.data['visualization_settings'] = settings
        self.save_data()


class GraphWidget(QWidget):
    """Widget för att visa grafer med zoom och navigation"""
    
    def __init__(self):
        super().__init__()
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        
        # Lägg till navigeringsverktyg (zoom, pan, reset)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)  # Lägg till toolbar först
        layout.addWidget(self.canvas)
        self.setLayout(layout)
    
    def plot_weight_progress(self, entries, profile, vis_settings=None):
        """Ritar viktförloppsgraf med prognos och optimal kurva"""
        self.figure.clear()
        
        if not entries:
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'Ingen data tillgänglig\nLägg till viktmätningar i "Lägg till vikt"-fliken',
                   ha='center', va='center', fontsize=12)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            self.canvas.draw()
            return
        
        # Extrahera data
        dates = [datetime.strptime(e['date'], '%Y-%m-%d') for e in entries]
        weights = [e['weight'] for e in entries]
        current_weight = weights[-1]
        current_date = dates[-1]
        
        ax = self.figure.add_subplot(111)
        
        # Visualiseringsinställningar
        if vis_settings is None:
            vis_settings = {
                'highlight_weekends': False,
                'highlight_days': [],
                'show_events': False,
                'custom_events': []
            }
        
        # Hitta min och max för y-axeln
        all_weights = weights.copy()
        if profile.get('target_weight'):
            all_weights.append(profile['target_weight'])
        if profile.get('start_weight'):
            all_weights.append(profile['start_weight'])
        y_min = min(all_weights) - 2
        y_max = max(all_weights) + 2
        
        # Rita helgmarkeringar om aktiverat
        if vis_settings.get('highlight_weekends', False):
            weekend_ranges = []
            for i, date in enumerate(dates):
                if date.weekday() >= 5:  # Lördag (5) eller Söndag (6)
                    weekend_ranges.append(date)
            
            # Hitta alla helger i datumintervallet
            start_date = dates[0]
            end_date = dates[-1]
            current = start_date
            first_weekend = True  # Lägg bara till label första gången
            while current <= end_date:
                if current.weekday() == 5:  # Lördag
                    # Rita en vertikal zon för helgen (lördag-söndag)
                    ax.axvspan(current, current + timedelta(days=2), 
                             alpha=0.1, color='#FFB6C1', zorder=0, label='Helg' if first_weekend else '')
                    first_weekend = False
                current += timedelta(days=1)
        
        # Rita markering för specifika veckodagar
        highlight_days = vis_settings.get('highlight_days', [])
        if highlight_days:
            day_colors = {
                0: '#FFE5B4',  # Måndag - Persika
                1: '#E0BBE4',  # Tisdag - Lila
                2: '#FFDAB9',  # Onsdag - Persika
                3: '#B4E5FF',  # Torsdag - Ljusblå
                4: '#C7CEEA',  # Fredag - Lavendel
                5: '#FFB6C1',  # Lördag - Rosa
                6: '#FFC1CC',  # Söndag - Rosa
            }
            day_names = ['Måndag', 'Tisdag', 'Onsdag', 'Torsdag', 'Fredag', 'Lördag', 'Söndag']
            
            first_marked_day = True  # Bara en label för alla markerade dagar
            for day_num in highlight_days:
                if day_num not in day_colors:
                    continue
                    
                # Hitta alla datum för denna veckodag
                start_date = dates[0]
                end_date = dates[-1]
                current = start_date
                
                while current <= end_date:
                    if current.weekday() == day_num:
                        ax.axvline(x=current, alpha=0.25, color=day_colors[day_num], 
                                 linewidth=2, linestyle='--', zorder=0,
                                 label='Markerade dagar' if first_marked_day else '')
                        first_marked_day = False
                    current += timedelta(days=1)
        
        # Rita anpassade händelser
        custom_events = vis_settings.get('custom_events', [])
        if vis_settings.get('show_events', True) and custom_events:
            for event in custom_events:
                try:
                    event_date = datetime.strptime(event['date'], '%Y-%m-%d')
                    if dates[0] <= event_date <= dates[-1]:
                        ax.axvline(x=event_date, alpha=0.4, color=event.get('color', '#FF6347'),
                                 linewidth=2, linestyle=':', zorder=1)
                        ax.text(event_date, y_max - 0.5, event['label'], 
                               rotation=90, va='top', ha='right', fontsize=8,
                               color=event.get('color', '#FF6347'), weight='bold')
                except:
                    pass  # Ignorera felaktiga händelser
        
        # Rita viktlinje
        ax.plot(dates, weights, 'o-', linewidth=2, markersize=8, 
               color='#2E86AB', label='Aktuell vikt', zorder=3)
        
        # Rita trendlinje och prognos
        if len(dates) > 1:
            x_numeric = [(d - dates[0]).days for d in dates]
            
            # Enkel linjär trend för historisk data
            z = np.polyfit(x_numeric, weights, 1)
            p = np.poly1d(z)
            trend_weights = [p(x) for x in x_numeric]
            ax.plot(dates, trend_weights, '--', linewidth=2, 
                   color='#A23B72', label='Linjär trend', alpha=0.7, zorder=2)
            
            # Förbättrad prognos med hybrid metod
            target_weight = profile.get('target_weight')
            if target_weight and target_weight < current_weight:
                weekly_change, weeks_to_goal, projected_date = predict_weight_improved(
                    dates, weights, target_weight, method='hybrid'
                )
                
                if weekly_change and projected_date:
                    # Rita prognoslinje med förbättrad metod
                    prognosis_dates = [current_date, projected_date]
                    prognosis_weights = [current_weight, target_weight]
                    ax.plot(prognosis_dates, prognosis_weights, ':', linewidth=2.5,
                           color='#8B4789', label=f'Prognos: {int(weeks_to_goal)} veckor', 
                           alpha=0.8, zorder=2)
                    
                    # Visa förväntad måldag
                    ax.plot(projected_date, target_weight, '*', markersize=15,
                           color='#8B4789', zorder=4)
                    ax.text(projected_date, target_weight, 
                           f'  {projected_date.strftime("%Y-%m-%d")}',
                           fontsize=9, va='center')
                    
                    # Lägg till exponentiell utjämning som referens
                    if len(weights) >= 5:
                        smoothed = exponential_smoothing(weights, alpha=0.3)
                        ax.plot(dates, smoothed, '-', linewidth=1.5, 
                               color='#FF6B9D', label='Exponentiell utjämning', 
                               alpha=0.5, zorder=1)
        
        # Rita optimal viktminskning (procentbaserad: 0.5-0.75% per vecka)
        target_weight = profile.get('target_weight')
        start_weight = profile.get('start_weight', weights[0])
        
        if target_weight and target_weight < start_weight:
            # Beräkna optimal kurva från första mätningen
            start_date = dates[0]
            weight_to_lose = start_weight - target_weight
            
            # Optimal: 0.5-0.75% av kroppsvikten per vecka
            # Vi använder 0.6% som optimal (mitt i spannet)
            optimal_weekly_percent = 0.006  # 0.6%
            
            # Beräkna optimal kurva vecka för vecka
            optimal_dates = [start_date]
            optimal_weights = [start_weight]
            current_optimal_weight = start_weight
            weeks = 0
            max_weeks = 104  # Max 2 år
            
            while current_optimal_weight > target_weight and weeks < max_weeks:
                weeks += 1
                # Minska med 0.6% av nuvarande vikt
                weekly_loss = current_optimal_weight * optimal_weekly_percent
                current_optimal_weight -= weekly_loss
                
                # Gå inte under målvikt
                if current_optimal_weight < target_weight:
                    current_optimal_weight = target_weight
                
                optimal_dates.append(start_date + timedelta(weeks=weeks))
                optimal_weights.append(current_optimal_weight)
            
            # Beräkna genomsnittlig viktminskning för label
            avg_weekly_loss = (start_weight - target_weight) / weeks if weeks > 0 else 0
            
            ax.plot(optimal_dates, optimal_weights, '--', linewidth=2,
                   color='#52B788', label=f'Optimal (0.5-0.75% av vikt/vecka)', 
                   alpha=0.7, zorder=1)
            
            # Fyll area mellan optimal och aktuell (bara om vi har tillräckligt med data)
            if len(dates) > 1 and len(optimal_dates) > 1:
                # Hitta gemensamt datumintervall
                min_date = max(dates[0], optimal_dates[0])
                max_date = min(dates[-1], optimal_dates[-1])
                
                if min_date <= max_date:
                    # Interpolera optimal vikt för varje mätdatum inom intervallet
                    optimal_interp = []
                    dates_in_range = []
                    
                    for i, d in enumerate(dates):
                        if min_date <= d <= max_date:
                            dates_in_range.append(d)
                            # Hitta närmaste optimal vikt
                            days_from_start = (d - optimal_dates[0]).days
                            weeks_from_start = days_from_start / 7
                            
                            # Hitta rätt position i optimal kurva
                            if weeks_from_start < len(optimal_weights):
                                week_idx = int(weeks_from_start)
                                if week_idx + 1 < len(optimal_weights):
                                    # Interpolera mellan veckor
                                    frac = weeks_from_start - week_idx
                                    opt_weight = optimal_weights[week_idx] * (1 - frac) + optimal_weights[week_idx + 1] * frac
                                else:
                                    opt_weight = optimal_weights[week_idx]
                            else:
                                opt_weight = target_weight
                            
                            optimal_interp.append(opt_weight)
                    
                    # Extrahera motsvarande faktiska vikter
                    actual_weights = [weights[i] for i, d in enumerate(dates) if min_date <= d <= max_date]
                    
                    if len(dates_in_range) > 0 and len(optimal_interp) == len(actual_weights):
                        # Fyll area
                        ax.fill_between(dates_in_range, actual_weights, optimal_interp, 
                                       where=[w >= o for w, o in zip(actual_weights, optimal_interp)],
                                       alpha=0.15, color='red', label='Över optimal')
                        ax.fill_between(dates_in_range, actual_weights, optimal_interp,
                                       where=[w < o for w, o in zip(actual_weights, optimal_interp)],
                                       alpha=0.15, color='green', label='Under optimal')
        
        # Rita målvikt
        if target_weight:
            ax.axhline(y=target_weight, color='#F18F01', 
                      linestyle=':', linewidth=2, label='Målvikt', zorder=1)
        
        # Rita startvikt
        if profile.get('start_weight'):
            ax.axhline(y=profile['start_weight'], color='#C73E1D', 
                      linestyle=':', linewidth=2, label='Startvikt', alpha=0.5, zorder=1)
        
        ax.set_xlabel('Datum', fontsize=11)
        ax.set_ylabel('Vikt (kg)', fontsize=11)
        ax.set_title('Viktförlopp med Prognos', fontsize=14, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best', fontsize=9)
        
        # Rotera datum för bättre läsbarhet
        self.figure.autofmt_xdate()
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_bmi_progress(self, entries, height):
        """Ritar BMI-utveckling"""
        self.figure.clear()
        
        if not entries or not height:
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'Ange längd i profilinställningar för BMI-graf',
                   ha='center', va='center', fontsize=12)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            self.canvas.draw()
            return
        
        dates = [datetime.strptime(e['date'], '%Y-%m-%d') for e in entries]
        weights = [e['weight'] for e in entries]
        height_m = height / 100
        bmis = [w / (height_m ** 2) for w in weights]
        
        ax = self.figure.add_subplot(111)
        
        # Rita BMI-linje
        ax.plot(dates, bmis, 'o-', linewidth=2, markersize=8, 
               color='#6A4C93', label='BMI')
        
        # BMI-kategorier
        ax.axhspan(0, 18.5, alpha=0.1, color='blue', label='Undervikt')
        ax.axhspan(18.5, 25, alpha=0.1, color='green', label='Normalvikt')
        ax.axhspan(25, 30, alpha=0.1, color='orange', label='Övervikt')
        ax.axhspan(30, 40, alpha=0.1, color='red', label='Fetma')
        
        ax.set_xlabel('Datum', fontsize=11)
        ax.set_ylabel('BMI', fontsize=11)
        ax.set_title('BMI-utveckling', fontsize=14, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best', fontsize=8)
        
        self.figure.autofmt_xdate()
        self.figure.tight_layout()
        self.canvas.draw()


class WeightTrackerApp(QMainWindow):
    """Huvudfönster för viktspårningsappen"""
    
    def __init__(self):
        super().__init__()
        self.weight_data = WeightData()
        self.init_ui()
        self.refresh_data()
    
    def init_ui(self):
        """Initierar användargränssnittet"""
        self.setWindowTitle('Viktspårnings App')
        self.setGeometry(100, 100, 1200, 800)
        
        # Centralt widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Titel
        title = QLabel('Viktspårning')
        title.setFont(QFont('Arial', 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet('color: #2E86AB; margin: 10px;')
        layout.addWidget(title)
        
        # Tabbad vy
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Lägg till flikar
        self.create_add_weight_tab()
        self.create_progress_tab()
        self.create_statistics_tab()
        self.create_history_tab()
        self.create_visualization_settings_tab()
        self.create_profile_tab()
    
    def create_add_weight_tab(self):
        """Skapar fliken för att lägga till vikt"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Formulär grupp
        form_group = QGroupBox('Ny viktmätning')
        form_layout = QFormLayout()
        
        # Datumväljare
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        form_layout.addRow('Datum:', self.date_edit)
        
        # Viktinmatning
        self.weight_input = QDoubleSpinBox()
        self.weight_input.setRange(30, 300)
        self.weight_input.setDecimals(1)
        self.weight_input.setSuffix(' kg')
        self.weight_input.setValue(70.0)
        form_layout.addRow('Vikt:', self.weight_input)
        
        # Anteckningar
        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText('Anteckningar (valfritt)')
        form_layout.addRow('Anteckningar:', self.notes_input)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Knapp för att lägga till
        add_button = QPushButton('Lägg till viktmätning')
        add_button.setStyleSheet('''
            QPushButton {
                background-color: #2E86AB;
                color: white;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1e5f7a;
            }
        ''')
        add_button.clicked.connect(self.add_weight)
        layout.addWidget(add_button)
        
        # Info-sektion
        info_group = QGroupBox('Senaste mätning')
        self.latest_info = QLabel('Ingen data ännu')
        self.latest_info.setFont(QFont('Arial', 11))
        self.latest_info.setStyleSheet('padding: 10px;')
        info_layout = QVBoxLayout()
        info_layout.addWidget(self.latest_info)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        self.tabs.addTab(tab, 'Lägg till vikt')
    
    def create_progress_tab(self):
        """Skapar fliken för viktförlopp"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        self.weight_graph = GraphWidget()
        layout.addWidget(self.weight_graph)
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, 'Viktförlopp')
    
    def create_statistics_tab(self):
        """Skapar fliken för BMI och statistik"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Statistik info
        stats_group = QGroupBox('Statistik')
        self.stats_label = QLabel()
        self.stats_label.setFont(QFont('Arial', 11))
        self.stats_label.setStyleSheet('padding: 10px;')
        stats_layout = QVBoxLayout()
        stats_layout.addWidget(self.stats_label)
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # BMI-graf
        self.bmi_graph = GraphWidget()
        layout.addWidget(self.bmi_graph)
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, 'BMI & Statistik')
    
    def create_history_tab(self):
        """Skapar fliken för historik"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Tabell
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(['Datum', 'Vikt (kg)', 'Anteckningar', 'Åtgärd'])
        self.history_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.history_table.setSortingEnabled(True)  # Gör tabellen sorterbar
        layout.addWidget(self.history_table)
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, 'Historik')
    
    def create_visualization_settings_tab(self):
        """Skapar fliken för visualiseringsinställningar"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Huvudrubrik
        title = QLabel('Anpassa Grafvisning')
        title.setFont(QFont('Arial', 16, QFont.Bold))
        title.setStyleSheet('color: #2E86AB; margin: 10px;')
        layout.addWidget(title)
        
        # Helgmarkering
        weekend_group = QGroupBox('Helgmarkering')
        weekend_layout = QVBoxLayout()
        self.weekend_checkbox = QCheckBox('Markera helger i grafen')
        self.weekend_checkbox.setChecked(True)
        self.weekend_checkbox.stateChanged.connect(self.auto_save_vis_settings)  # Auto-spara
        weekend_info = QLabel('💡 Helger (lördag-söndag) markeras med ljusrosa bakgrund')
        weekend_info.setStyleSheet('color: #666; font-style: italic; margin-left: 20px;')
        weekend_layout.addWidget(self.weekend_checkbox)
        weekend_layout.addWidget(weekend_info)
        weekend_group.setLayout(weekend_layout)
        layout.addWidget(weekend_group)
        
        # Veckodag-markeringar
        weekday_group = QGroupBox('Markera Specifika Veckodagar')
        weekday_layout = QVBoxLayout()
        
        info_label = QLabel('✨ Använd detta för att se mönster kopplade till specifika dagar:')
        info_label.setStyleSheet('font-weight: bold; margin-bottom: 5px;')
        weekday_layout.addWidget(info_label)
        
        examples = QLabel(
            '• Fastedagar (ex. måndagar)\n'
            '• Träningsdagar (ex. tisdagar och torsdagar)\n'
            '• Cheatdays (ex. fredagar)\n'
            '• Vägningsdagar (för att se när du brukar väga dig)'
        )
        examples.setStyleSheet('color: #666; margin-left: 10px; margin-bottom: 10px;')
        weekday_layout.addWidget(examples)
        
        self.weekday_checkboxes = {}
        weekdays = ['Måndag', 'Tisdag', 'Onsdag', 'Torsdag', 'Fredag', 'Lördag', 'Söndag']
        weekday_colors = ['#FFE5B4', '#E0BBE4', '#FFDAB9', '#B4E5FF', '#C7CEEA', '#FFB6C1', '#FFC1CC']
        
        for i, (day, color) in enumerate(zip(weekdays, weekday_colors)):
            cb = QCheckBox(f'{day}ar')
            cb.setStyleSheet(f'QCheckBox::indicator:checked {{ background-color: {color}; }}')
            cb.stateChanged.connect(self.auto_save_vis_settings)  # Auto-spara
            self.weekday_checkboxes[i] = cb
            weekday_layout.addWidget(cb)
        
        weekday_group.setLayout(weekday_layout)
        layout.addWidget(weekday_group)
        
        # Anpassade händelser
        events_group = QGroupBox('Anpassade Händelser')
        events_layout = QVBoxLayout()
        
        events_info = QLabel(
            '📌 Markera viktiga händelser i grafen:\n'
            '• Födelsedagar, semester, stress-perioder\n'
            '• Sjukdom, skador, livsstilsändringar\n'
            '• Start av nytt träningsprogram'
        )
        events_info.setStyleSheet('color: #666; margin-bottom: 10px;')
        events_layout.addWidget(events_info)
        
        self.show_events_checkbox = QCheckBox('Visa händelser i grafen')
        self.show_events_checkbox.setChecked(True)
        self.show_events_checkbox.stateChanged.connect(self.auto_save_vis_settings)  # Auto-spara
        events_layout.addWidget(self.show_events_checkbox)
        
        # Lägg till händelse-sektion
        add_event_layout = QHBoxLayout()
        
        self.event_date_edit = QDateEdit()
        self.event_date_edit.setDate(QDate.currentDate())
        self.event_date_edit.setCalendarPopup(True)
        add_event_layout.addWidget(QLabel('Datum:'))
        add_event_layout.addWidget(self.event_date_edit)
        
        self.event_label_edit = QLineEdit()
        self.event_label_edit.setPlaceholderText('Ex: Semester, Sjuk, Ny träning')
        add_event_layout.addWidget(QLabel('Händelse:'))
        add_event_layout.addWidget(self.event_label_edit)
        
        add_event_btn = QPushButton('Lägg till')
        add_event_btn.clicked.connect(self.add_custom_event)
        add_event_btn.setStyleSheet('background-color: #52B788; color: white; padding: 5px;')
        add_event_layout.addWidget(add_event_btn)
        
        events_layout.addLayout(add_event_layout)
        
        # Lista över händelser
        self.events_list = QTableWidget()
        self.events_list.setColumnCount(3)
        self.events_list.setHorizontalHeaderLabels(['Datum', 'Händelse', 'Ta bort'])
        self.events_list.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.events_list.setMaximumHeight(150)
        events_layout.addWidget(self.events_list)
        
        events_group.setLayout(events_layout)
        layout.addWidget(events_group)
        
        # Ingen spara-knapp - sparas automatiskt
        
        layout.addStretch()
        tab.setLayout(layout)
        self.tabs.addTab(tab, 'Grafanpassning')
    
    def create_profile_tab(self):
        """Skapar fliken för profilinställningar"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        form_group = QGroupBox('Profilinställningar')
        form_layout = QFormLayout()
        
        # Längd
        self.height_input = QSpinBox()
        self.height_input.setRange(100, 250)
        self.height_input.setSuffix(' cm')
        self.height_input.setValue(170)
        form_layout.addRow('Längd:', self.height_input)
        
        # Målvikt
        self.target_weight_input = QDoubleSpinBox()
        self.target_weight_input.setRange(30, 300)
        self.target_weight_input.setDecimals(1)
        self.target_weight_input.setSuffix(' kg')
        self.target_weight_input.setValue(70.0)
        form_layout.addRow('Målvikt:', self.target_weight_input)
        
        # Startvikt
        self.start_weight_input = QDoubleSpinBox()
        self.start_weight_input.setRange(30, 300)
        self.start_weight_input.setDecimals(1)
        self.start_weight_input.setSuffix(' kg')
        self.start_weight_input.setValue(80.0)
        form_layout.addRow('Startvikt:', self.start_weight_input)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Spara-knapp
        save_button = QPushButton('Spara profil')
        save_button.setStyleSheet('''
            QPushButton {
                background-color: #F18F01;
                color: white;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c97301;
            }
        ''')
        save_button.clicked.connect(self.save_profile)
        layout.addWidget(save_button)
        
        layout.addStretch()
        tab.setLayout(layout)
        self.tabs.addTab(tab, 'Profil')
    
    def add_weight(self):
        """Lägger till en ny viktmätning"""
        date = self.date_edit.date().toString('yyyy-MM-dd')
        weight = self.weight_input.value()
        notes = self.notes_input.text()
        
        self.weight_data.add_entry(date, weight, notes)
        self.notes_input.clear()
        QMessageBox.information(self, 'Sparad', f'Vikt {weight} kg sparad för {date}')
        self.refresh_data()
    
    def save_profile(self):
        """Sparar profilinställningar"""
        height = self.height_input.value()
        target = self.target_weight_input.value()
        start = self.start_weight_input.value()
        
        self.weight_data.set_profile(height, target, start)
        QMessageBox.information(self, 'Sparad', 'Profil uppdaterad!')
        self.refresh_data()
    
    def add_custom_event(self):
        """Lägger till en anpassad händelse"""
        date = self.event_date_edit.date().toString('yyyy-MM-dd')
        label = self.event_label_edit.text().strip()
        
        if not label:
            QMessageBox.warning(self, 'Felaktig inmatning', 'Ange en händelse!')
            return
        
        # Lägg till i temporär lista (sparas vid save_vis_settings)
        vis_settings = self.weight_data.get_vis_settings()
        if 'custom_events' not in vis_settings:
            vis_settings['custom_events'] = []
        
        # Slumpmässig färg för händelsen
        colors = ['#FF6347', '#FF1493', '#9370DB', '#20B2AA', '#FF8C00', '#DC143C']
        import random
        color = random.choice(colors)
        
        vis_settings['custom_events'].append({
            'date': date,
            'label': label,
            'color': color
        })
        
        self.weight_data.set_vis_settings(vis_settings)
        self.event_label_edit.clear()
        self.load_vis_settings()
        self.refresh_data()
    
    def delete_custom_event(self, index):
        """Tar bort en anpassad händelse"""
        vis_settings = self.weight_data.get_vis_settings()
        if 'custom_events' in vis_settings and index < len(vis_settings['custom_events']):
            del vis_settings['custom_events'][index]
            self.weight_data.set_vis_settings(vis_settings)
            self.load_vis_settings()
            self.refresh_data()
    
    def save_vis_settings(self):
        """Sparar visualiseringsinställningar"""
        vis_settings = self.weight_data.get_vis_settings()
        
        # Helgmarkering
        vis_settings['highlight_weekends'] = self.weekend_checkbox.isChecked()
        
        # Veckodagar
        highlight_days = []
        for day_num, checkbox in self.weekday_checkboxes.items():
            if checkbox.isChecked():
                highlight_days.append(day_num)
        vis_settings['highlight_days'] = highlight_days
        
        # Händelser
        vis_settings['show_events'] = self.show_events_checkbox.isChecked()
        
        self.weight_data.set_vis_settings(vis_settings)
        QMessageBox.information(self, 'Sparad', 'Visualiseringsinställningar uppdaterade!')
        self.refresh_data()
    
    def auto_save_vis_settings(self):
        """Sparar visualiseringsinställningar automatiskt utan meddelande"""
        vis_settings = self.weight_data.get_vis_settings()
        
        # Helgmarkering
        vis_settings['highlight_weekends'] = self.weekend_checkbox.isChecked()
        
        # Veckodagar
        highlight_days = []
        for day_num, checkbox in self.weekday_checkboxes.items():
            if checkbox.isChecked():
                highlight_days.append(day_num)
        vis_settings['highlight_days'] = highlight_days
        
        # Händelser
        vis_settings['show_events'] = self.show_events_checkbox.isChecked()
        
        self.weight_data.set_vis_settings(vis_settings)
        self.refresh_data()  # Uppdatera grafen direkt
    
    def load_vis_settings(self):
        """Laddar visualiseringsinställningar till UI"""
        vis_settings = self.weight_data.get_vis_settings()
        
        # Helgmarkering
        self.weekend_checkbox.setChecked(vis_settings.get('highlight_weekends', True))
        
        # Veckodagar
        highlight_days = vis_settings.get('highlight_days', [])
        for day_num, checkbox in self.weekday_checkboxes.items():
            checkbox.setChecked(day_num in highlight_days)
        
        # Händelser
        self.show_events_checkbox.setChecked(vis_settings.get('show_events', True))
        
        # Uppdatera händelselista
        custom_events = vis_settings.get('custom_events', [])
        self.events_list.setRowCount(len(custom_events))
        
        for i, event in enumerate(custom_events):
            self.events_list.setItem(i, 0, QTableWidgetItem(event['date']))
            self.events_list.setItem(i, 1, QTableWidgetItem(event['label']))
            
            delete_btn = QPushButton('Ta bort')
            delete_btn.setStyleSheet('background-color: #C73E1D; color: white;')
            delete_btn.clicked.connect(lambda checked, idx=i: self.delete_custom_event(idx))
            self.events_list.setCellWidget(i, 2, delete_btn)
    
    def delete_entry_dialog(self, date):
        """Bekräftar borttagning av mätning"""
        reply = QMessageBox.question(self, 'Bekräfta borttagning',
                                    f'Vill du ta bort mätningen från {date}?',
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.weight_data.delete_entry(date)
            self.refresh_data()
    
    def refresh_data(self):
        """Uppdaterar alla vyer med ny data"""
        entries = self.weight_data.get_entries()
        profile = self.weight_data.get_profile()
        vis_settings = self.weight_data.get_vis_settings()
        
        # Uppdatera profilformulär
        if profile:
            self.height_input.setValue(profile.get('height', 170))
            self.target_weight_input.setValue(profile.get('target_weight', 70))
            self.start_weight_input.setValue(profile.get('start_weight', 80))
        
        # Ladda visualiseringsinställningar
        self.load_vis_settings()
        
        # Uppdatera senaste info
        if entries:
            latest = entries[-1]
            info_text = f"<b>Datum:</b> {latest['date']}<br>"
            info_text += f"<b>Vikt:</b> {latest['weight']} kg<br>"
            if latest.get('notes'):
                info_text += f"<b>Anteckningar:</b> {latest['notes']}<br>"
            
            if profile.get('height'):
                height_m = profile['height'] / 100
                bmi = latest['weight'] / (height_m ** 2)
                info_text += f"<b>BMI:</b> {bmi:.1f}"
            
            self.latest_info.setText(info_text)
        else:
            self.latest_info.setText('Ingen data ännu')
        
        # Uppdatera grafer med visualiseringsinställningar
        self.weight_graph.plot_weight_progress(entries, profile, vis_settings)
        self.bmi_graph.plot_bmi_progress(entries, profile.get('height'))
        
        # Uppdatera statistik
        self.update_statistics(entries, profile)
        
        # Uppdatera historik-tabell
        self.update_history_table(entries)
    
    def update_statistics(self, entries, profile):
        """Uppdaterar statistikvisning med prognos"""
        if not entries:
            self.stats_label.setText('Ingen data tillgänglig')
            return
        
        weights = [e['weight'] for e in entries]
        dates = [datetime.strptime(e['date'], '%Y-%m-%d') for e in entries]
        current = weights[-1]
        current_date = dates[-1]
        start = profile.get('start_weight', weights[0])
        target = profile.get('target_weight', 0)
        
        total_change = current - start
        remaining = current - target if target else 0
        avg_weight = sum(weights) / len(weights)
        
        # Beräkna trendvikt per vecka
        if len(entries) > 1:
            days = (dates[-1] - dates[0]).days
            if days > 0:
                weekly_change = (weights[-1] - weights[0]) / days * 7
            else:
                weekly_change = 0
        else:
            weekly_change = 0
        
        stats = f"<h3 style='color: #2E86AB;'>📊 Aktuell Status</h3>"
        stats += f"<b>Aktuell vikt:</b> {current} kg<br>"
        stats += f"<b>Startvikt:</b> {start} kg<br>"
        
        if target:
            stats += f"<b>Målvikt:</b> {target} kg<br>"
            stats += f"<b>Kvar till mål:</b> {abs(remaining):.1f} kg<br>"
        
        stats += f"<b>Total förändring:</b> {total_change:+.1f} kg<br>"
        stats += f"<b>Genomsnittsvikt:</b> {avg_weight:.1f} kg<br>"
        
        stats += f"<h3 style='color: #A23B72;'>📈 Trend & Prognos</h3>"
        
        # Enkel linjär trend för översikt
        stats += f"<b>Linjär trend per vecka:</b> {weekly_change:+.2f} kg ({abs(weekly_change/current*100):.2f}% av vikt)<br>"
        
        # Förbättrad prognos
        if target and remaining > 0:
            weekly_change_pred, weeks_to_goal_pred, projected_date_pred = predict_weight_improved(
                dates, weights, target, method='hybrid'
            )

            days_to_goal = None
            if weekly_change_pred and weekly_change_pred < 0:
                days_to_goal = int(weeks_to_goal_pred * 7)

                stats += f"<b>Förbättrad prognos (Hybrid-modell):</b><br>"
                stats += f"  • Förväntad hastighet: {abs(weekly_change_pred):.2f} kg/vecka<br>"
                stats += f"  • Beräknad tid till mål: {int(weeks_to_goal_pred)} veckor ({days_to_goal} dagar)<br>"
                stats += f"  • Beräknad måldag: {projected_date_pred.strftime('%Y-%m-%d')}<br>"

                # Visa osäkerhet baserat på datamängd
                if len(entries) < 10:
                    confidence = "Låg"
                    conf_color = "#F18F01"
                    conf_note = "Behöver mer data för exakt prognos"
                elif len(entries) < 20:
                    confidence = "Medel"
                    conf_color = "#F18F01"
                    conf_note = "Relativt pålitlig prognos"
                else:
                    confidence = "Hög"
                    conf_color = "#52B788"
                    conf_note = "Mycket pålitlig prognos"

                stats += f"  • Säkerhet: <span style='color: {conf_color};'>{confidence}</span> ({conf_note})<br>"

            # Jämför med optimal hastighet (procentbaserad)
            # Optimal: 0.5-0.75% av kroppsvikten per vecka
            weekly_loss_percent = abs(weekly_change / current * 100)
            optimal_min_percent = 0.5
            optimal_max_percent = 0.75
            optimal_mid_percent = 0.6

            # Beräkna optimal tid med procentbaserad metod
            optimal_weeks = 0
            optimal_weight = current
            while optimal_weight > target and optimal_weeks < 200:
                optimal_weeks += 1
                optimal_weight -= optimal_weight * (optimal_mid_percent / 100)
            optimal_days = int(optimal_weeks * 7)

            if weekly_loss_percent > optimal_max_percent + 0.15:
                status = "⚠️ För snabb"
                advice = f"Du går ner {weekly_loss_percent:.2f}% per vecka. Rekommenderat: 0.5-0.75% av din kroppsvikt"
                color = "#C73E1D"
            elif weekly_loss_percent < optimal_min_percent - 0.15:
                status = "🐌 För långsam"
                advice = f"Du går ner {weekly_loss_percent:.2f}% per vecka. Optimalt: 0.5-0.75% av din kroppsvikt"
                color = "#F18F01"
            else:
                status = "✅ Perfekt takt"
                advice = f"Du går ner {weekly_loss_percent:.2f}% per vecka - en hälsosam och hållbar viktminskning!"
                color = "#52B788"

            stats += f"<br><b>Status:</b> <span style='color: {color};'>{status}</span><br>"
            stats += f"<i>{advice}</i><br>"

            stats += f"<br><b>Optimal takt (0.5-0.75% av vikt/vecka):</b><br>"
            stats += f"  • Tid till mål: {int(optimal_weeks)} veckor ({optimal_days} dagar)<br>"
            stats += f"  • Förväntad förlust nu: {current * optimal_mid_percent / 100:.2f} kg/vecka<br>"

            if days_to_goal is not None:
                if days_to_goal < optimal_days:
                    diff = optimal_days - days_to_goal
                    stats += f"  • Du är {diff} dagar <span style='color: #C73E1D;'>snabbare</span> än optimalt<br>"
                elif days_to_goal > optimal_days:
                    diff = days_to_goal - optimal_days
                    stats += f"  • Du är {diff} dagar <span style='color: #F18F01;'>långsammare</span> än optimalt<br>"
                else:
                    stats += f"  • Du ligger <span style='color: #52B788;'>perfekt</span> i fas!<br>"
        
        elif target and remaining > 0 and weekly_change >= 0:
            stats += f"<b style='color: #C73E1D;'>⚠️ Vikten ökar eller är stabil</b><br>"
            stats += f"<i>För att nå målet behöver vikten minska</i><br>"
        
        stats += f"<h3 style='color: #6A4C93;'>📝 Allmänt</h3>"
        stats += f"<b>Antal mätningar:</b> {len(entries)}<br>"
        
        if len(entries) > 1:
            days_tracked = (dates[-1] - dates[0]).days
            stats += f"<b>Dagar spårade:</b> {days_tracked}<br>"
        
        if profile.get('height'):
            height_m = profile['height'] / 100
            bmi = current / (height_m ** 2)
            stats += f"<b>Aktuell BMI:</b> {bmi:.1f}"
            
            if bmi < 18.5:
                category = "Undervikt"
                cat_color = "#4A90E2"
            elif bmi < 25:
                category = "Normalvikt"
                cat_color = "#52B788"
            elif bmi < 30:
                category = "Övervikt"
                cat_color = "#F18F01"
            else:
                category = "Fetma"
                cat_color = "#C73E1D"
            stats += f" (<span style='color: {cat_color};'>{category}</span>)"
        
        self.stats_label.setText(stats)
    
    def update_history_table(self, entries):
        """Uppdaterar historik-tabellen"""
        self.history_table.setSortingEnabled(False)  # Stäng av sortering under uppdatering
        self.history_table.setRowCount(len(entries))
        
        # Visa äldst först (ta bort reversed)
        for i, entry in enumerate(entries):
            self.history_table.setItem(i, 0, QTableWidgetItem(entry['date']))
            self.history_table.setItem(i, 1, QTableWidgetItem(str(entry['weight'])))
            self.history_table.setItem(i, 2, QTableWidgetItem(entry.get('notes', '')))
            
            # Ta bort-knapp
            delete_btn = QPushButton('Ta bort')
            delete_btn.setStyleSheet('background-color: #C73E1D; color: white;')
            delete_btn.clicked.connect(lambda checked, d=entry['date']: self.delete_entry_dialog(d))
            self.history_table.setCellWidget(i, 3, delete_btn)
        
        self.history_table.setSortingEnabled(True)  # Aktivera sortering igen


def main():
    app = QApplication(sys.argv)
    
    # Stil för hela applikationen
    app.setStyle('Fusion')
    
    window = WeightTrackerApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
