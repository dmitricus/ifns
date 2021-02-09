from rest_framework import serializers

from ifns.helpers import validate_code
from ifns.models import Setting, Requisites


class SettingSerializer(serializers.ModelSerializer):
    base_url = serializers.SerializerMethodField()
    current_config = serializers.SerializerMethodField()

    class Meta:
        model = Setting
        fields = ('base_url', 'current_config')

    def get_base_url(self, obj):
        return obj.current_config.get('base_url', None)

    def get_current_config(self, obj):
        return obj.current_config.get('current_config', None)


class RequisitesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requisites
        fields = (
            'nalog_code',
            'name',
            'address',
            'phone',
            'additional_Info',
            'payment_receiver',
            'OKTMO_code',
            'receiver_inn',
            'receiver_kpp',
            'bank_name',
            'bank_account_bik',
            'bank_account_corr',
            'bank_account_number',
            'registration_code',
            'registration_name',
            'registration_address',
            'registration_phone',
            'registration_add_Info',
            'registration_code_2',
            'registration_name_2',
            'registration_address_2',
            'registration_phone_2',
            'registration_add_Info_2',
        )


class CodeIfnsSerializer(serializers.Serializer):
    code = serializers.CharField(min_length=4, max_length=4, validators=[validate_code])
