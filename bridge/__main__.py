"""python -m bridge 로 실행할 수 있도록 하는 엔트리포인트"""

from bridge.main import main
import asyncio

try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
