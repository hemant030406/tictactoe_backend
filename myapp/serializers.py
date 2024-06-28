from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','name','code','moves','undo_stack',)
        extra_kwargs = {
            'code': {'write_only': True}
        }
    
    def create(self, validated_data):
        code = validated_data.pop('code',None)
        instance = self.Meta.model(**validated_data)
        if code is not None:
            instance.set_password(code)
        instance.save()
        return instance