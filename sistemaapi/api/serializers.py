
from rest_framework import serializers

from sistemaapi.models import Equipo, Deporte, Liga, Partido, Apuesta, EventoPartido


class EquipoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipo
        fields = '__all__'

class DeporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deporte
        fields = '__all__'

class LigaSerializer(serializers.ModelSerializer):
    deporte = DeporteSerializer(read_only=True)
    deporte_id = serializers.PrimaryKeyRelatedField(
        queryset=Deporte.objects.all(),
        source='deporte',
        write_only=True
    )

    class Meta:
        model = Liga
        fields = ['id', 'nombre', 'deporte', 'deporte_id', 'logo']

class PartidoSerializer(serializers.ModelSerializer):
    equipo1 = EquipoSerializer(read_only=True)
    equipo2 = EquipoSerializer(read_only=True)
    liga = LigaSerializer(read_only=True)

    # Para permitir enviar IDs al crear o actualizar
    equipo1_id = serializers.PrimaryKeyRelatedField(
        queryset=Equipo.objects.all(), source='equipo1', write_only=True
    )
    equipo2_id = serializers.PrimaryKeyRelatedField(
        queryset=Equipo.objects.all(), source='equipo2', write_only=True
    )
    liga_id = serializers.PrimaryKeyRelatedField(
        queryset=Liga.objects.all(), source='liga', write_only=True
    )

    class Meta:
        model = Partido
        fields = [
            'id',
            'equipo1', 'equipo1_id',
            'equipo2', 'equipo2_id',
            'liga', 'liga_id',
            'marcador1',
            'marcador2',
            'fecha_hora',
            'duracion_minutos',
            'estado'
        ]

    # Valores por defecto al crear un nuevo partido
    def create(self, validated_data):
        validated_data['marcador1'] = validated_data.get('marcador1', 0)
        validated_data['marcador2'] = validated_data.get('marcador2', 0)
        validated_data['estado'] = validated_data.get('estado', 0)  # 0 representa 'Pendiente'
        return super().create(validated_data)

class ApuestaSerializer(serializers.ModelSerializer):
    partido = PartidoSerializer(read_only=True)
    partido_id = serializers.PrimaryKeyRelatedField(
        queryset=Partido.objects.all(),
        source='partido',
        write_only=True
    )
    equipo = EquipoSerializer(read_only=True)
    equipo_id = serializers.PrimaryKeyRelatedField(
        queryset=Equipo.objects.all(),
        source='equipo',
        write_only=True
    )

    class Meta:
        model = Apuesta
        fields = ['id', 'usuario_id', 'partido', 'partido_id', 'tipo_apuesta', 'monto', 'equipo', 'equipo_id', 'estado', 'created_at', 'multiplicador']

class PartidoResumenSerializer(serializers.ModelSerializer):
    resumen = serializers.SerializerMethodField()

    class Meta:
        model = Partido
        fields = ['id', 'resumen']

    def get_resumen(self, obj):
        return f"{obj.equipo1.nombre} vs {obj.equipo2.nombre}"


class EventoPartidoSerializer(serializers.ModelSerializer):
    partido = PartidoResumenSerializer(read_only=True)
    equipo = EquipoSerializer(read_only=True)

    # Para permitir enviar los IDs al crear o actualizar
    partido_id = serializers.PrimaryKeyRelatedField(
        queryset=Partido.objects.all(), source='partido', write_only=True
    )
    equipo_id = serializers.PrimaryKeyRelatedField(
        queryset=Equipo.objects.all(), source='equipo', write_only=True
    )

    class Meta:
        model = EventoPartido
        fields = [
            'id',
            'partido', 'partido_id',
            'descripcion',
            'equipo', 'equipo_id',
            'minuto'
        ]
