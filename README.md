# formcheck

**FormCheck — AI Personal Trainer. Real-time exercise form correction using pose estimation.**

![Build](https://img.shields.io/badge/build-passing-brightgreen) ![License](https://img.shields.io/badge/license-proprietary-red)

## Install
```bash
pip install -e ".[dev]"
```

## Quick Start
```python
from src.core import Formcheck
 instance = Formcheck()
r = instance.learn(input="test")
```

## CLI
```bash
python -m src status
python -m src run --input "data"
```

## API
| Method | Description |
|--------|-------------|
| `learn()` | Learn |
| `assess()` | Assess |
| `recommend()` | Recommend |
| `track_progress()` | Track progress |
| `generate_exercise()` | Generate exercise |
| `certify()` | Certify |
| `get_stats()` | Get stats |
| `reset()` | Reset |

## Test
```bash
pytest tests/ -v
```

## License
(c) 2026 Officethree Technologies. All Rights Reserved.
