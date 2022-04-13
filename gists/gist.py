import typing


__all__ = ("Gist",)


class Gist:
    def __init__(self, data: typing.Dict, client: "Client"):
        self.data = data
        self.client = client
        # Set the data dict's items as attributes
        self._update_attrs(data)

    def _update_attrs(self, data: typing.Dict):
        """Update the Gist object's attributes to the provided data"""

        # TODO use getter and setters to do this, the current way is not good practise
        self.__dict__.update(data)

    async def update(self):
        """Fetch and update the Gist object with the gist"""

        updated_gist_data = await self.client.update_gist(self.id)
        self._update_attrs(updated_gist_data)

    async def edit(self, *, files: typing.Dict, description: str = None):
        """Edit the gist associated with the Gist object, then update the Gist object"""

        edited_gist_data = await self.client.edit_gist(
            self.id, files=files, description=description
        )
        self._update_attrs(edited_gist_data)

    async def delete(self):
        """Delete the gist associated with the Gist object, then delete the Gist object itself"""

        await self.client.delete_gist(self.id)
        del self
