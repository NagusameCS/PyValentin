"""
Copyright (c) 2025
This program is part of PyValentin
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License.
"""

import pygame
import pygame.gfxdraw
import sys
import os
import csv
from core.FixCSV import replace_values_in_csv
from core.Ski import process_csv, calculate_distances, calculate_similarity, save_processed_data
from core.analysis import MatchAnalysis
import json
from typing import Dict, Tuple, List, Optional
import time
import os.path
from pathlib import Path

# Initialize Pygame
pygame.init()

# VS Code-inspired color scheme
COLORS = {
    'background': (30, 30, 30),        # VS Code dark background
    'widget_bg': (37, 37, 38),         # Slightly lighter than background
    'button': (14, 99, 156),           # VS Code blue
    'button_hover': (0, 122, 204),     # VS Code bright blue
    'button_active': (0, 88, 156),     # Darker blue for clicks
    'text': (204, 204, 204),           # VS Code text color
    'text_disabled': (110, 110, 110),  # Dimmed text
    'border': (64, 64, 64),            # Widget borders
    'error': (255, 88, 88),            # Error text
    'success': (80, 200, 120),         # Success text
    'warning': (228, 157, 42),         # Warning text
    'progress_bar': (0, 122, 204),     # Progress indicator
    'progress_bg': (45, 45, 45),       # Progress background
    'slider_handle': (119, 119, 119),  # Slider handle
}

ACCEPTED_EXTENSIONS = {
    'csv': ['.csv'],
    'config': ['.json'],
    'filter': ['.json'],
    'grade': ['.csv']
}

def draw_rounded_rect(surface, rect, color, radius=8):
    """Draw a rounded rectangle by combining multiple shapes"""
    if radius > rect.height // 2:
        radius = rect.height // 2
    if radius > rect.width // 2:
        radius = rect.width // 2

    rect = pygame.Rect(rect)
    
    # Create alpha surface for antialiasing
    surf = pygame.Surface(rect.size, pygame.SRCALPHA)
    
    # Draw the main rectangle
    r = rect.copy()
    r.topleft = (0, 0)
    pygame.draw.rect(surf, (*color, 255), r.inflate(-radius*2, 0))
    pygame.draw.rect(surf, (*color, 255), r.inflate(0, -radius*2))
    
    # Draw the four corner circles
    ellipse_rect = pygame.Rect(0, 0, radius * 2, radius * 2)
    
    # Top left
    ellipse_rect.topleft = (r.left, r.top)
    pygame.draw.ellipse(surf, (*color, 255), ellipse_rect)
    
    # Top right
    ellipse_rect.topright = (r.right, r.top)
    pygame.draw.ellipse(surf, (*color, 255), ellipse_rect)
    
    # Bottom right
    ellipse_rect.bottomright = (r.right, r.bottom)
    pygame.draw.ellipse(surf, (*color, 255), ellipse_rect)
    
    # Bottom left
    ellipse_rect.bottomleft = (r.left, r.bottom)
    pygame.draw.ellipse(surf, (*color, 255), ellipse_rect)
    
    # Blit the surface onto the target
    surface.blit(surf, rect)

class ModernButton:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False
        self.active = True
        self.font = pygame.font.SysFont('Segoe UI', 14)
        self.anim_progress = 0  # For hover animation
        self.clicked = False

    def draw(self, surface: pygame.Surface):
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)
        
        # Background color with animation
        if self.hovered:
            self.anim_progress = min(1.0, self.anim_progress + 0.2)
        else:
            self.anim_progress = max(0.0, self.anim_progress - 0.1)
            
        base_color = COLORS['button'] if self.active else COLORS['widget_bg']
        hover_color = COLORS['button_hover'] if self.active else COLORS['widget_bg']
        current_color = [
            int(base_color[i] + (hover_color[i] - base_color[i]) * self.anim_progress)
            for i in range(3)
        ]
        
        # Draw button with shadow effect
        shadow_rect = self.rect.copy()
        shadow_rect.y += 2
        pygame.gfxdraw.box(surface, shadow_rect, (0, 0, 0, 50))
        
        # Main button body
        draw_rounded_rect(surface, self.rect, current_color, 6)
        
        # Text
        text_color = COLORS['text'] if self.active else COLORS['text_disabled']
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        """Handle mouse events for the button"""
        if not self.active:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.rect.collidepoint(event.pos):
                    self.clicked = True
                    if self.action:
                        self.action()
                    return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.clicked = False
        
        return False

class ModernSlider:
    def __init__(self, x: int, y: int, width: int, height: int, label: str, initial_value: float = 0.5):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.value = initial_value
        self.dragging = False
        self.font = pygame.font.SysFont('Segoe UI', 14)
        self.handle_rect = pygame.Rect(0, 0, 12, height + 8)
        self.clicked = False  # Add this line
        
    def draw(self, surface: pygame.Surface):
        # Draw label and value
        label_text = f"{self.label}: {self.value:.2f}"
        label_surface = self.font.render(label_text, True, COLORS['text'])
        surface.blit(label_surface, (self.rect.x, self.rect.y - 20))
        
        # Draw track background
        track_rect = pygame.Rect(self.rect.x, self.rect.centery - 2, self.rect.width, 4)
        draw_rounded_rect(surface, track_rect, COLORS['widget_bg'], 2)
        
        # Draw active track portion
        active_width = int(self.value * self.rect.width)
        active_rect = pygame.Rect(self.rect.x, self.rect.centery - 2, active_width, 4)
        if active_width > 0:
            draw_rounded_rect(surface, active_rect, COLORS['button'], 2)
        
        # Draw handle
        handle_x = self.rect.x + int(self.value * self.rect.width) - self.handle_rect.width // 2
        self.handle_rect.centerx = handle_x + self.handle_rect.width // 2
        self.handle_rect.centery = self.rect.centery
        draw_rounded_rect(surface, self.handle_rect, COLORS['slider_handle'], 6)

    def handle_event(self, event):
        """Handle mouse events for the slider"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.handle_rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            # Update slider value based on mouse position
            mouse_x = event.pos[0]
            rel_x = max(0, min(mouse_x - self.rect.x, self.rect.width))
            self.value = rel_x / self.rect.width

class ModernProgressBar:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.progress = 0
        
    def draw(self, surface: pygame.Surface):
        # Draw background
        draw_rounded_rect(surface, self.rect, COLORS['progress_bg'], 4)
        
        # Draw progress
        if self.progress > 0:
            progress_width = int(self.rect.width * self.progress)
            progress_rect = pygame.Rect(self.rect.x, self.rect.y, progress_width, self.rect.height)
            draw_rounded_rect(surface, progress_rect, COLORS['progress_bar'], 4)

# Define window size at the top level
WINDOW_SIZE = (800, 600)

class PyValentinGUI:
    def __init__(self):
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("PyValentin")
        
        # Initialize UI layout
        self.layout_ui()
        
        self.status_message = "Please select all required files"
        self.status_color = COLORS['warning']
        self.files = {'csv': None, 'config': None, 'filter': None, 'grade': None}
        self.dragging_file = False
        self.drag_pos = None
        
    def layout_ui(self):
        """Create modern VS Code-like layout"""
        padding = 20
        button_width = 250
        button_height = 36
        
        # Center content in window
        start_x = (800 - button_width) // 2
        start_y = 80
        
        # Create modern buttons with consistent spacing
        self.buttons = {
            'csv': ModernButton(start_x, start_y, button_width, button_height, 
                              "Select CSV File", self.select_csv),
            'config': ModernButton(start_x, start_y + 60, button_width, button_height, 
                                 "Select Config File", self.select_config),
            'filter': ModernButton(start_x, start_y + 120, button_width, button_height, 
                                 "Select Filter File", self.select_filter),
            'grade': ModernButton(start_x, start_y + 180, button_width, button_height, 
                                "Select Grade CSV", self.select_grade),
        }
        
        # Sliders with proper spacing
        self.quality_slider = ModernSlider(start_x, start_y + 260, button_width, 8, 
                                         "Quality Weight", 0.5)
        self.grade_slider = ModernSlider(start_x, start_y + 320, button_width, 8, 
                                       "Grade Weight", 0.7)
        
        # Process button at bottom
        self.buttons['process'] = ModernButton(start_x, start_y + 400, button_width, button_height,
                                             "Process Files", self.process_files)
        self.buttons['process'].active = False
        
        # Progress bar at bottom
        self.progress_bar = ModernProgressBar(padding, 550, 800 - padding * 2, 8)

    def select_csv(self):
        path = self.file_dialog("CSV files", "*.csv")
        if path:
            self.files['csv'] = path
            self.update_status()
            
    def select_config(self):
        path = self.file_dialog("JSON files", "*.json")
        if path:
            self.files['config'] = path
            self.update_status()
            
    def select_filter(self):
        path = self.file_dialog("JSON files", "*.json")
        if path:
            self.files['filter'] = path
            self.update_status()
            
    def select_grade(self):
        path = self.file_dialog("CSV files", "*.csv")
        if path:
            self.files['grade'] = path
            self.update_status()
            
    def file_dialog(self, description: str, extension: str) -> Optional[str]:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            filetypes=[(description, extension)]
        )
        return file_path if file_path else None
        
    def update_status(self):
        if all(self.files.values()):
            self.status_message = "Ready to process"
            self.status_color = COLORS['success']
            self.buttons['process'].active = True
        else:
            self.status_message = "Please select all required files"
            self.status_color = COLORS['warning']
            self.buttons['process'].active = False
            
    def process_files(self):
        if not all(self.files.values()):
            return
            
        try:
            # Stage 1: Initialize and process CSV
            self.status_message = "Stage 1/5: Processing CSV..."
            self.progress_bar.progress = 0.2
            self.draw()
            
            output_dir = os.path.join(os.path.dirname(__file__), "core", "genR")
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, "modified_csv.csv")
            
            replace_values_in_csv(self.files['csv'], self.files['config'], output_file)
            
            # Stage 2: Calculate distances
            self.status_message = "Stage 2/5: Calculating distances..."
            self.progress_bar.progress = 0.4
            self.draw()
            
            data = process_csv(output_file)
            distances = calculate_distances(data)
            save_processed_data(distances, os.path.join(output_dir, "processed_distances.csv"))
            
            # Stage 3: Compute similarities
            self.status_message = "Stage 3/5: Computing similarities..."
            self.progress_bar.progress = 0.6
            self.draw()
            
            similarity = calculate_similarity(distances)
            save_processed_data(similarity, os.path.join(output_dir, "similarity_list.csv"))
            
            # Stage 4: Filter matches
            self.status_message = "Stage 4/5: Filtering matches..."
            self.progress_bar.progress = 0.8
            self.draw()
            
            # Stage 5: Create pairs
            self.status_message = "Stage 5/5: Creating optimal pairs..."
            self.progress_bar.progress = 1.0
            self.draw()
            
            # Analysis
            analyzer = MatchAnalysis(output_dir)
            analyzer.analyze_all_algorithms()
            
            self.status_message = "Processing completed! Check core/genR folder"
            self.status_color = COLORS['success']
            
        except Exception as e:
            self.status_message = f"Error: {str(e)}"
            self.status_color = COLORS['error']
            self.progress_bar.progress = 0
            
    def handle_drag_and_drop(self, event):
        """Handle file drag and drop events"""
        if event.type == pygame.DROPFILE:
            filepath = event.file
            extension = os.path.splitext(filepath)[1].lower()
            
            # Determine which button the file was dropped closest to
            closest_button = None
            min_distance = float('inf')
            
            for button_type, button in self.buttons.items():
                if button_type == 'process':  # Skip process button
                    continue
                    
                # Calculate distance to button center
                button_center = button.rect.center
                if self.drag_pos:  # Use last known drag position
                    distance = ((button_center[0] - self.drag_pos[0]) ** 2 + 
                              (button_center[1] - self.drag_pos[1]) ** 2) ** 0.5
                    
                    # Check if extension matches button type
                    if extension in ACCEPTED_EXTENSIONS[button_type]:
                        if distance < min_distance:
                            min_distance = distance
                            closest_button = button_type
            
            if closest_button:
                self.files[closest_button] = filepath
                self.update_status()
                
        elif event.type == pygame.MOUSEMOTION:
            self.drag_pos = event.pos
    
    def draw(self):
        self.screen.fill(COLORS['background'])
        
        # Draw buttons
        for button in self.buttons.values():
            button.draw(self.screen)
            
        # Draw sliders
        self.quality_slider.draw(self.screen)
        self.grade_slider.draw(self.screen)
        
        # Draw progress bar
        self.progress_bar.draw(self.screen)
        
        # Draw status message
        font = pygame.font.SysFont('Segoe UI', 18)  # Changed from Font(None, 24)
        status_surface = font.render(self.status_message, True, self.status_color)
        status_rect = status_surface.get_rect(center=(WINDOW_SIZE[0]//2, WINDOW_SIZE[1]-30))
        self.screen.blit(status_surface, status_rect)
        
        # Add drag-and-drop hint text when no files are selected
        if not all(self.files.values()):
            hint_font = pygame.font.SysFont('Segoe UI', 14)
            hint_text = "Drag and drop files onto buttons to upload"
            hint_surface = hint_font.render(hint_text, True, COLORS['text_disabled'])
            hint_rect = hint_surface.get_rect(center=(WINDOW_SIZE[0]//2, WINDOW_SIZE[1]-60))
            self.screen.blit(hint_surface, hint_rect)
        
        pygame.display.flip()
        
    def run(self):
        running = True
        clock = pygame.time.Clock()  # Add this line for consistent frame rate
        
        # Enable file drop
        pygame.event.set_allowed([pygame.DROPFILE])
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.DROPFILE:
                    self.handle_drag_and_drop(event)
                elif event.type == pygame.MOUSEMOTION and self.dragging_file:
                    self.handle_drag_and_drop(event)
                else:
                    # Handle button events
                    for button in self.buttons.values():
                        button.handle_event(event)
                    
                    # Handle slider events
                    self.quality_slider.handle_event(event)
                    self.grade_slider.handle_event(event)
                
            self.draw()
            clock.tick(60)  # Limit to 60 FPS
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = PyValentinGUI()
    app.run()
