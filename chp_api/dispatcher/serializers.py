from rest_framework import serializers
from .models import Transaction

class TransactionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
                'id',
                'date_time',
                'status',
                ]

class TransactionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
                'id',
                'date_time',
                'query',
                'status',
                ]
