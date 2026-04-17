from workers import WorkerEntrypoint

from worldometer_api import ApiRouter


class Default(WorkerEntrypoint):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._router = ApiRouter()

    async def fetch(self, request):
        return await self._router.handle(request)
