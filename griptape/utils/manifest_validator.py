from schema import Schema


class ManifestValidator:
    def validate(self, manifest: dict) -> dict:
        return self.schema().validate(manifest)

    def schema(self) -> Schema:
        return Schema({"version": "v1", "name": str, "description": str, "contact_email": str, "legal_info_url": str})
