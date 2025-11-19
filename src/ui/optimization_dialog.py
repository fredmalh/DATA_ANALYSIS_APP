"""
Optimization Dialog Module
Dialog for configuring optimization parameters.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QCheckBox, QScrollArea, QWidget, QMessageBox,
    QDoubleSpinBox, QGroupBox, QRadioButton, QButtonGroup, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from typing import List, Dict, Any, Optional
import pandas as pd


class OptimizationDialog(QDialog):
    """Dialog for configuring optimization parameters."""
    
    def __init__(self, data: pd.DataFrame, parent=None, saved_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the optimization dialog.
        
        Args:
            data: DataFrame containing the data
            parent: Parent window
        """
        super().__init__(parent)
        self.data = data
        self.numeric_columns = [col for col in data.columns 
                               if pd.api.types.is_numeric_dtype(data[col])]
        
        self.target_combos = []
        self.direction_buttons = []  # List of button groups, one per target
        self.constraint_checkboxes = []
        self.constraint_spinboxes = []
        self.weight_spinboxes = []
        self.input_checkboxes = {}
        
        self.setWindowTitle("Optimization Configuration")
        self.setMinimumSize(700, 800)
        self.resize(800, 900)
        
        # Set window flags
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowCloseButtonHint
        )
        
        # Apply dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #212121;
            }
            QLabel {
                color: #FFFFFF;
            }
            QComboBox {
                background-color: #303030;
                color: #FFFFFF;
                border: 1px solid #424242;
                border-radius: 4px;
                padding: 5px;
                min-height: 20px;
            }
            QComboBox:hover {
                border-color: #64B5F6;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #303030;
                color: #FFFFFF;
                selection-background-color: #0d47a1;
            }
            QCheckBox {
                color: #FFFFFF;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #64B5F6;
                border-radius: 3px;
                background-color: #303030;
            }
            QCheckBox::indicator:checked {
                background-color: #0d47a1;
                border-color: #0d47a1;
            }
            QDoubleSpinBox {
                background-color: #303030;
                color: #FFFFFF;
                border: 1px solid #424242;
                border-radius: 4px;
                padding: 5px;
            }
            QGroupBox {
                color: #FFFFFF;
                border: 1px solid #424242;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QRadioButton {
                color: #FFFFFF;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #64B5F6;
                border-radius: 9px;
                background-color: #303030;
            }
            QRadioButton::indicator:checked {
                background-color: #0d47a1;
                border-color: #0d47a1;
            }
        """)
        
        self._init_ui()
        
        # Load saved configuration if provided
        if saved_config:
            self._load_configuration(saved_config)
    
    def _load_configuration(self, config: Dict[str, Any]):
        """Load a saved configuration into the dialog."""
        # Load target variables, directions, and weights together
        target_variables = config.get('target_variables', [])
        optimization_directions = config.get('optimization_directions', [])
        weights = config.get('weights', [])
        
        # Load targets into combo boxes (use first N available slots)
        for i, target in enumerate(target_variables):
            if i < len(self.target_combos) and target:
                index = self.target_combos[i].findData(target)
                if index >= 0:
                    self.target_combos[i].setCurrentIndex(index)
                    
                    # Load direction for this target
                    if i < len(optimization_directions):
                        direction = optimization_directions[i]
                        if direction == 'maximize':
                            self.direction_buttons[i].button(0).setChecked(True)
                        else:
                            self.direction_buttons[i].button(1).setChecked(True)
                    
                    # Load weight for this target
                    if i < len(weights):
                        self.weight_spinboxes[i].setValue(weights[i])
        
        # Load constraints - constraints are now stored by target variable name
        constraints = config.get('constraints', {})
        for combo_box_idx, combo in enumerate(self.target_combos):
            target_name = combo.currentData()
            if target_name and target_name in constraints:
                constraint = constraints[target_name]
                self.constraint_checkboxes[combo_box_idx].setChecked(True)
                constraint_type = constraint.get('type', '>')
                constraint_value = constraint.get('value', 0.0)
                # Find and set constraint type in combo
                combo_constraint = self.constraint_combos[combo_box_idx]
                for i in range(combo_constraint.count()):
                    if combo_constraint.itemData(i) == constraint_type:
                        combo_constraint.setCurrentIndex(i)
                        break
                self.constraint_spinboxes[combo_box_idx].setValue(constraint_value)
        
        # Load input variables
        input_variables = config.get('input_variables', [])
        for col, checkbox in self.input_checkboxes.items():
            checkbox.setChecked(col in input_variables)
    
    def _init_ui(self):
        """Build and display the dialog UI."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)
        
        # Title
        title_label = QLabel("Optimization Configuration")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: white; padding-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #424242;
                border-radius: 5px;
                background-color: #212121;
            }
        """)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setSpacing(15)
        content_widget.setLayout(content_layout)
        
        # Combined Target Variables, Constraints & Weights Section
        targets_group = QGroupBox("Target Variables, Constraints & Weights (Select 1-5)")
        targets_layout = QVBoxLayout()
        targets_layout.setSpacing(5)  # Reduced spacing to bring titles closer to blocks
        
        # Create header row for clarity
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        
        # Target Variable header
        target_header = QLabel("Target Variable")
        target_header.setStyleSheet("font-weight: bold; color: #64B5F6; padding: 5px;")
        header_layout.addWidget(target_header, stretch=2)
        
        # Direction header
        direction_header = QLabel("Direction")
        direction_header.setStyleSheet("font-weight: bold; color: #64B5F6; padding: 5px;")
        header_layout.addWidget(direction_header, stretch=1)
        
        # Constraint header
        constraint_header = QLabel("Constraint (Optional)")
        constraint_header.setStyleSheet("font-weight: bold; color: #64B5F6; padding: 5px;")
        header_layout.addWidget(constraint_header, stretch=2)
        
        # Weight header
        weight_header = QLabel("Weight")
        weight_header.setStyleSheet("font-weight: bold; color: #64B5F6; padding: 5px;")
        header_layout.addWidget(weight_header, stretch=1)
        
        targets_layout.addLayout(header_layout)
        
        # Main horizontal layout for the 4 blocks
        blocks_layout = QHBoxLayout()
        blocks_layout.setSpacing(5)
        
        # Create constraints combo boxes list
        self.constraint_combos = []  # Store combo boxes for constraint signs
        
        # === Block 1: Target Variable Container ===
        target_block_container = QWidget()
        target_block_container.setStyleSheet("""
            QWidget {
                background-color: #2a2a2a;
                border: 1px solid #424242;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        target_block_layout = QVBoxLayout()
        target_block_layout.setContentsMargins(10, 10, 10, 10)
        target_block_layout.setSpacing(10)
        
        # === Block 2: Direction Container ===
        direction_block_container = QWidget()
        direction_block_container.setStyleSheet("""
            QWidget {
                background-color: #2a2a2a;
                border: 1px solid #424242;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        direction_block_layout = QVBoxLayout()
        direction_block_layout.setContentsMargins(10, 10, 10, 10)
        direction_block_layout.setSpacing(10)
        
        # === Block 3: Constraint Container ===
        constraint_block_container = QWidget()
        constraint_block_container.setStyleSheet("""
            QWidget {
                background-color: #2a2a2a;
                border: 1px solid #424242;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        constraint_block_layout = QVBoxLayout()
        constraint_block_layout.setContentsMargins(10, 10, 10, 10)
        constraint_block_layout.setSpacing(10)
        
        # === Block 4: Weight Container ===
        weight_block_container = QWidget()
        weight_block_container.setStyleSheet("""
            QWidget {
                background-color: #2a2a2a;
                border: 1px solid #424242;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        weight_block_layout = QVBoxLayout()
        weight_block_layout.setContentsMargins(10, 10, 10, 10)
        weight_block_layout.setSpacing(10)
        
        # Create rows for each block
        for i in range(5):
            # Row in Block 1: Target Variable
            target_row_layout = QHBoxLayout()
            target_row_layout.setSpacing(10)
            target_label = QLabel(f"Target {i+1}:")
            target_label.setMinimumWidth(70)
            target_row_layout.addWidget(target_label)
            
            target_combo = QComboBox()
            target_combo.addItem("-- Select Variable --", None)
            for col in self.numeric_columns:
                target_combo.addItem(col, col)
            self.target_combos.append(target_combo)
            target_row_layout.addWidget(target_combo, stretch=1)
            target_block_layout.addLayout(target_row_layout)
            
            # Row in Block 2: Direction
            direction_row_layout = QHBoxLayout()
            direction_row_layout.setSpacing(10)
            direction_group = QButtonGroup()
            max_radio = QRadioButton("Max")
            min_radio = QRadioButton("Min")
            max_radio.setChecked(True)  # Default to maximize
            direction_group.addButton(max_radio, 0)
            direction_group.addButton(min_radio, 1)
            self.direction_buttons.append(direction_group)
            direction_row_layout.addWidget(max_radio)
            direction_row_layout.addWidget(min_radio)
            direction_row_layout.addStretch()
            direction_block_layout.addLayout(direction_row_layout)
            
            # Row in Block 3: Constraint
            constraint_row_layout = QHBoxLayout()
            constraint_row_layout.setSpacing(10)
            constraint_check = QCheckBox("")
            constraint_check.setChecked(False)  # Default disabled
            self.constraint_checkboxes.append(constraint_check)
            
            constraint_combo = QComboBox()
            constraint_combo.addItem(">", ">")
            constraint_combo.addItem(">=", ">=")
            constraint_combo.addItem("<", "<")
            constraint_combo.addItem("<=", "<=")
            constraint_combo.addItem("=", "==")
            constraint_combo.setEnabled(False)
            self.constraint_combos.append(constraint_combo)
            
            # Set default values based on original requirements
            if i == 1:  # Target 2
                constraint_check.setChecked(True)
                constraint_combo.setCurrentIndex(0)  # >
                default_value = 0.0
            elif i == 2:  # Target 3
                constraint_check.setChecked(True)
                constraint_combo.setCurrentIndex(0)  # >
                default_value = 1.0
            elif i == 3:  # Target 4
                constraint_check.setChecked(True)
                constraint_combo.setCurrentIndex(0)  # >
                default_value = 0.0
            else:
                default_value = 0.0
            
            constraint_spin = QDoubleSpinBox()
            constraint_spin.setValue(default_value)
            constraint_spin.setDecimals(1)
            constraint_spin.setRange(-1e10, 1e10)
            constraint_spin.setEnabled(constraint_check.isChecked())
            self.constraint_spinboxes.append(constraint_spin)
            
            constraint_check.toggled.connect(
                lambda checked, combo=constraint_combo, spin=constraint_spin: 
                self._toggle_constraint(checked, combo, spin)
            )
            
            constraint_row_layout.addWidget(constraint_check)
            constraint_row_layout.addWidget(constraint_combo)
            constraint_row_layout.addWidget(constraint_spin)
            constraint_block_layout.addLayout(constraint_row_layout)
            
            # Row in Block 4: Weight
            weight_row_layout = QHBoxLayout()
            weight_spin = QDoubleSpinBox()
            weight_spin.setValue(1.0)
            weight_spin.setDecimals(2)
            weight_spin.setRange(0.0, 100.0)
            weight_spin.setSingleStep(0.1)
            self.weight_spinboxes.append(weight_spin)
            weight_row_layout.addWidget(weight_spin)
            weight_block_layout.addLayout(weight_row_layout)
        
        # Set layouts to containers
        target_block_container.setLayout(target_block_layout)
        direction_block_container.setLayout(direction_block_layout)
        constraint_block_container.setLayout(constraint_block_layout)
        weight_block_container.setLayout(weight_block_layout)
        
        # Add containers to main blocks layout
        blocks_layout.addWidget(target_block_container, stretch=2)
        blocks_layout.addWidget(direction_block_container, stretch=1)
        blocks_layout.addWidget(constraint_block_container, stretch=2)
        blocks_layout.addWidget(weight_block_container, stretch=1)
        
        targets_layout.addLayout(blocks_layout)
        targets_group.setLayout(targets_layout)
        content_layout.addWidget(targets_group)
        
        # Input Variables Section
        inputs_group = QGroupBox("Input Variables (Select at least 1)")
        inputs_layout = QVBoxLayout()
        inputs_layout.setSpacing(10)
        
        inputs_info = QLabel("Select the input variables to consider:")
        inputs_info.setStyleSheet("color: #BDBDBD; font-size: 12px;")
        inputs_layout.addWidget(inputs_info)
        
        # Scroll area for input checkboxes
        inputs_scroll = QScrollArea()
        inputs_scroll.setWidgetResizable(True)
        inputs_scroll.setMaximumHeight(200)
        inputs_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #424242;
                border-radius: 5px;
                background-color: #212121;
            }
        """)
        
        inputs_widget = QWidget()
        inputs_main_layout = QHBoxLayout()
        inputs_main_layout.setSpacing(10)
        inputs_main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create four columns
        inputs_col1_layout = QVBoxLayout()
        inputs_col1_layout.setSpacing(5)
        inputs_col2_layout = QVBoxLayout()
        inputs_col2_layout.setSpacing(5)
        inputs_col3_layout = QVBoxLayout()
        inputs_col3_layout.setSpacing(5)
        inputs_col4_layout = QVBoxLayout()
        inputs_col4_layout.setSpacing(5)
        
        # Distribute checkboxes across four columns
        for idx, col in enumerate(self.numeric_columns):
            checkbox = QCheckBox(col)
            self.input_checkboxes[col] = checkbox
            # Distribute across 4 columns
            if idx % 4 == 0:
                inputs_col1_layout.addWidget(checkbox)
            elif idx % 4 == 1:
                inputs_col2_layout.addWidget(checkbox)
            elif idx % 4 == 2:
                inputs_col3_layout.addWidget(checkbox)
            else:
                inputs_col4_layout.addWidget(checkbox)
        
        inputs_col1_layout.addStretch()
        inputs_col2_layout.addStretch()
        inputs_col3_layout.addStretch()
        inputs_col4_layout.addStretch()
        
        inputs_main_layout.addLayout(inputs_col1_layout)
        inputs_main_layout.addLayout(inputs_col2_layout)
        inputs_main_layout.addLayout(inputs_col3_layout)
        inputs_main_layout.addLayout(inputs_col4_layout)
        inputs_widget.setLayout(inputs_main_layout)
        inputs_scroll.setWidget(inputs_widget)
        inputs_layout.addWidget(inputs_scroll)
        
        inputs_group.setLayout(inputs_layout)
        content_layout.addWidget(inputs_group)
        
        content_layout.addStretch()
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #424242;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                min-height: 32px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        run_button = QPushButton("Run Optimization")
        run_button.setStyleSheet("""
            QPushButton {
                background-color: #0d47a1;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                min-height: 32px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:pressed {
                background-color: #0a3d91;
            }
        """)
        run_button.clicked.connect(self._on_run_clicked)
        button_layout.addWidget(run_button)
        
        layout.addLayout(button_layout)
    
    def _toggle_constraint(self, checked: bool, combo: QComboBox, spin: QDoubleSpinBox):
        """Enable/disable constraint controls based on checkbox state."""
        combo.setEnabled(checked)
        spin.setEnabled(checked)
    
    def _on_run_clicked(self):
        """Handle run button click."""
        # Validate inputs
        error = self._validate_inputs()
        if error:
            QMessageBox.warning(self, "Validation Error", error)
            return
        
        self.accept()
    
    def _validate_inputs(self) -> Optional[str]:
        """Validate user inputs."""
        # Check at least one target is selected (1-5 allowed)
        target_variables = []
        for i, combo in enumerate(self.target_combos):
            target = combo.currentData()
            if target is not None:
                if target in target_variables:
                    return f"Each target variable must be unique."
                target_variables.append(target)
        
        if len(target_variables) == 0:
            return "At least one target variable must be selected."
        
        if len(target_variables) > 5:
            return "Maximum 5 target variables allowed."
        
        # Check at least one input is selected
        selected_inputs = [col for col, checkbox in self.input_checkboxes.items() 
                          if checkbox.isChecked()]
        if len(selected_inputs) == 0:
            return "At least one input variable must be selected."
        
        # Check no overlap between targets and inputs
        if set(target_variables) & set(selected_inputs):
            return "Target variables and input variables cannot overlap."
        
        return None
    
    def get_configuration(self) -> Dict[str, Any]:
        """Get the optimization configuration."""
        # Get target variables (filter out None values - only selected targets)
        target_variables = []
        optimization_directions = []
        weights = []
        
        for i, combo in enumerate(self.target_combos):
            target = combo.currentData()
            if target is not None:  # Only include selected targets
                target_variables.append(target)
                
                # Get direction for this target
                button_group = self.direction_buttons[i]
                if button_group.checkedId() == 0:  # Max radio button
                    optimization_directions.append('maximize')
                else:  # Min radio button
                    optimization_directions.append('minimize')
                
                # Get weight for this target
                weights.append(self.weight_spinboxes[i].value())
        
        # Get constraints - store by target variable name (not index)
        constraints = {}
        for combo_box_idx in range(5):
            target = self.target_combos[combo_box_idx].currentData()
            # Only add constraint if target is selected AND constraint is enabled
            if target is not None and self.constraint_checkboxes[combo_box_idx].isChecked():
                constraint_type = self.constraint_combos[combo_box_idx].currentData()
                constraint_value = self.constraint_spinboxes[combo_box_idx].value()
                constraints[target] = {  # Use target variable name as key
                    'type': constraint_type,
                    'value': constraint_value
                }
        
        # Get input variables
        input_variables = [col for col, checkbox in self.input_checkboxes.items() 
                          if checkbox.isChecked()]
        
        return {
            'target_variables': target_variables,
            'optimization_directions': optimization_directions,
            'constraints': constraints,
            'weights': weights,
            'input_variables': input_variables
        }

