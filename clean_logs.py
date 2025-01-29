import re
from pathlib import Path
import os
import shutil
from collections import defaultdict

def clean_logs(input_dir: str = "logs", output_dir: str = "cleaned_logs"):
    """Nettoie les logs en supprimant timestamps, données binaires et répétitions."""
    Path(output_dir).mkdir(exist_ok=True)
    
    # Pattern qui match tout ce qui ressemble à du binaire/hex
    binary_pattern = re.compile(r'(?:b\'[\x00-\xff]+\'|\\x[0-9a-fA-F]{2}|[^[:print:]])')
    # Pattern pour le timestamp
    timestamp_pattern = re.compile(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} - ')
    
    for log_file in Path(input_dir).glob("*.log"):
        clean_file = Path(output_dir) / f"{log_file.stem}_clean.log"
        
        line_counts = defaultdict(int)
        
        with open(log_file) as f:
            for line in f:
                # Enlève le timestamp
                line = timestamp_pattern.sub('', line)
                
                if any(trigger in line for trigger in ["raw:", "data=", "\\x", "decoded:"]):
                    # Nettoie les données binaires
                    clean_line = binary_pattern.split(line)[0] + "[DONNÉES BINAIRES]\n"
                    line_counts[clean_line] += 1
                else:
                    line_counts[line] += 1
        
        with open(clean_file, 'w') as out:
            for line, count in line_counts.items():
                if count > 1:
                    out.write(f"{line.rstrip()} (répété {count} fois)\n")
                else:
                    out.write(line)

def organize_logs():
    """Organise les logs en les déplaçant dans un dossier 'logs'."""
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Déplacer tous les fichiers .log du dossier courant vers le dossier logs
    current_dir = Path(".")
    for log_file in current_dir.glob("*.log"):
        if log_file.parent == current_dir:  # Ne déplacer que les fichiers du dossier courant
            try:
                shutil.move(str(log_file), str(logs_dir / log_file.name))
                print(f"Déplacé {log_file.name} vers {logs_dir}")
            except Exception as e:
                print(f"Erreur lors du déplacement de {log_file.name}: {str(e)}")

if __name__ == "__main__":
    # D'abord organiser les logs
    organize_logs()
    
    # Ensuite les nettoyer
    clean_logs() 