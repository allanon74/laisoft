from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .models import (
    Tema, Vista, Mansione, MansioneTranslation, Attivita, AttivitaTranslation,
    Priorita, PrioritaTranslation, Anno, Squadra, SquadraTranslation, Tipologia,
    TipologiaTranslation, Collaboratore, CdC, CdCTranslation, Struttura, StrutturaTranslation,
    Diritto, Evento, Tag, EventoTranslation, Segnalazione, Intervento, Team,
    Foto, Lavoro, TempiLavoro, Allegato, Annotazione, EventoSegnalazione,
    CollaboratoreMansione, CollaboratoreAssenza, CollaboratoreReperibilita
)

from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')

class TokenSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Token
        fields = ('key', 'user')
        



class TemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tema
        fields = '__all__'

class VistaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vista
        fields = '__all__'

class MansioneTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MansioneTranslation
        fields = '__all__'

class MansioneSerializer(serializers.ModelSerializer):
    translations = MansioneTranslationSerializer(many=True, read_only=True)
    class Meta:
        model = Mansione
        fields = '__all__'

class AttivitaTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttivitaTranslation
        fields = '__all__'

class AttivitaSerializer(serializers.ModelSerializer):
    translations = AttivitaTranslationSerializer(many=True, read_only=True)
    mansioni = serializers.PrimaryKeyRelatedField(many=True, queryset=Mansione.objects.all())
    class Meta:
        model = Attivita
        fields = '__all__'

class PrioritaTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrioritaTranslation
        fields = '__all__'

class PrioritaSerializer(serializers.ModelSerializer):
    translations = PrioritaTranslationSerializer(many=True, read_only=True)
    class Meta:
        model = Priorita
        fields = '__all__'

class AnnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anno
        fields = '__all__'

class SquadraTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SquadraTranslation
        fields = '__all__'

class SquadraSerializer(serializers.ModelSerializer):
    translations = SquadraTranslationSerializer(many=True, read_only=True)
    class Meta:
        model = Squadra
        fields = '__all__'

class TipologiaTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipologiaTranslation
        fields = '__all__'

class TipologiaSerializer(serializers.ModelSerializer):
    translations = TipologiaTranslationSerializer(many=True, read_only=True)
    class Meta:
        model = Tipologia
        fields = '__all__'

class CollaboratoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collaboratore
        fields = '__all__'

class CdCTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CdCTranslation
        fields = '__all__'

class CdCSerializer(serializers.ModelSerializer):
    translations = CdCTranslationSerializer(many=True, read_only=True)
    class Meta:
        model = CdC
        fields = '__all__'

class StrutturaTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = StrutturaTranslation
        fields = '__all__'

class StrutturaSerializer(serializers.ModelSerializer):
    translations = StrutturaTranslationSerializer(many=True, read_only=True)
    autorizzati = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = Struttura
        fields = '__all__'

class DirittoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diritto
        fields = '__all__'

class EventoTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventoTranslation
        fields = '__all__'

class EventoSerializer(serializers.ModelSerializer):
    translations = EventoTranslationSerializer(many=True, read_only=True)
    class Meta:
        model = Evento
        fields = '__all__'

class TagSerializer(EventoSerializer):
    class Meta(EventoSerializer.Meta):
        pass

class SegnalazioneSerializer(serializers.ModelSerializer):
    struttura = serializers.PrimaryKeyRelatedField(queryset=Struttura.objects.all())
    origine = serializers.PrimaryKeyRelatedField(many=False, queryset=Tipologia.objects.filter(tipo="SO"), required=False, allow_null=True)
    eventi = serializers.PrimaryKeyRelatedField(many=True, queryset=Evento.objects.all())
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all(), required=False, allow_null=True)
    tipo = serializers.PrimaryKeyRelatedField(queryset=Tipologia.objects.filter(tipo="ST"))
    
    class Meta:
        model = Segnalazione
        fields = '__all__'
        
class SegnalazioneCompletaSerializer(serializers.ModelSerializer):
    struttura = StrutturaSerializer(many=False, read_only=True)
    origine = TipologiaSerializer(many=False, read_only=True, required=False, allow_null=True)
    eventi = EventoSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True, required=False, allow_null=True)
    tipo = TipologiaSerializer(many=False, read_only=True)
    
    class Meta:
        model = Segnalazione
        fields = '__all__'

class InterventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Intervento
        fields = '__all__'

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'

class FotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Foto
        fields = '__all__'

class LavoroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lavoro
        fields = '__all__'

class TempiLavoroSerializer(serializers.ModelSerializer):
    class Meta:
        model = TempiLavoro
        fields = '__all__'

class AllegatoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Allegato
        fields = '__all__'

class AnnotazioneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Annotazione
        fields = '__all__'

class EventoSegnalazioneSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventoSegnalazione
        fields = '__all__'

class CollaboratoreMansioneSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollaboratoreMansione
        fields = '__all__'

class CollaboratoreAssenzaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollaboratoreAssenza
        fields = '__all__'

class CollaboratoreReperibilitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollaboratoreReperibilita
        fields = '__all__'
        

class AuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField(label="Username")
    password = serializers.CharField(label="Password", style={'input_type': 'password'}, trim_whitespace=False)
