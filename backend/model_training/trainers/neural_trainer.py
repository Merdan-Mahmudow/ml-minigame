"""Тренер для нейросетевых моделей (N-BEATS/N-HiTS)"""
import torch
import torch.nn as nn
from typing import Dict, Any, Tuple
import numpy as np


class SimpleTimeSeriesNN(nn.Module):
    """Простая нейросетевая модель для временных рядов"""
    
    def __init__(self, input_size: int, hidden_size: int = 128, num_layers: int = 2, output_size: int = 1):
        super(SimpleTimeSeriesNN, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)
    
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        output = self.fc(lstm_out[:, -1, :])
        return output


class NeuralTrainer:
    """Тренер для нейросетевых моделей"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {
            'hidden_size': 128,
            'num_layers': 2,
            'learning_rate': 0.001,
            'batch_size': 32,
            'epochs': 50
        }
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    def train(self, X_train, y_train, X_val=None, y_val=None) -> nn.Module:
        """Обучение модели"""
        input_size = X_train.shape[-1]
        model = SimpleTimeSeriesNN(
            input_size=input_size,
            hidden_size=self.config['hidden_size'],
            num_layers=self.config['num_layers']
        ).to(self.device)
        
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=self.config['learning_rate'])
        
        # Преобразование данных
        X_train_tensor = torch.FloatTensor(X_train).to(self.device)
        y_train_tensor = torch.FloatTensor(y_train).to(self.device)
        
        if X_val is not None and y_val is not None:
            X_val_tensor = torch.FloatTensor(X_val).to(self.device)
            y_val_tensor = torch.FloatTensor(y_val).to(self.device)
        
        # Обучение
        for epoch in range(self.config['epochs']):
            model.train()
            optimizer.zero_grad()
            outputs = model(X_train_tensor)
            loss = criterion(outputs.squeeze(), y_train_tensor)
            loss.backward()
            optimizer.step()
            
            if X_val is not None and y_val is not None and epoch % 10 == 0:
                model.eval()
                with torch.no_grad():
                    val_outputs = model(X_val_tensor)
                    val_loss = criterion(val_outputs.squeeze(), y_val_tensor)
                    print(f"Epoch {epoch}, Train Loss: {loss.item():.4f}, Val Loss: {val_loss.item():.4f}")
        
        return model
    
    def predict(self, model: nn.Module, X) -> np.ndarray:
        """Прогнозирование"""
        model.eval()
        X_tensor = torch.FloatTensor(X).to(self.device)
        with torch.no_grad():
            predictions = model(X_tensor)
        return predictions.cpu().numpy()
    
    def save_model(self, model: nn.Module, path: str):
        """Сохранение модели"""
        torch.save(model.state_dict(), path)
    
    def load_model(self, path: str, input_size: int) -> nn.Module:
        """Загрузка модели"""
        model = SimpleTimeSeriesNN(input_size=input_size)
        model.load_state_dict(torch.load(path))
        model.eval()
        return model

