from rest_framework import serializers
from rest_framework.authtoken.models import Token
# from parler_rest.serializers import TranslatableModelSerializer, TranslatedFieldsField

from .models import (
    Tema, Vista, Mansione, MansioneTranslation, Attivita, AttivitaTranslation,
    Priorita, PrioritaTranslation, Anno, Squadra, SquadraTranslation, Tipologia,
    TipologiaTranslation, Collaboratore, CdC, CdCTranslation, Struttura, StrutturaTranslation,
    Diritto, Evento, Tag, EventoTranslation, Segnalazione, Intervento, Team,
    Foto, Lavoro, TempiLavoro, Allegato, Annotazione, EventoSegnalazione,
    CollaboratoreMansione, CollaboratoreAssenza, CollaboratoreReperibilita
)

from django.contrib.auth.models import User


# Base struttura campi

_f_base = ('id', 'data_creazione', 'data_modifica', )
_f_gis = ('id', 'data_creazione', 'data_modifica', )
_f_itde = ('colore', 'fa_icon', 'fa_visible', 'translations', )
_f_periodic = ('periodico', 'periodo', 'cicli', 'duplicare', )
_f_description = ('oggetto', 'descrizione', 'note', )
_f_valid_date = ('data_da', 'data_a', )
_f_status = ('stato', )
_f_d3  = ('id_documento', )
_f_rabs = ('id_rabs', )



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
        fields = _f_base + ('modello', 'tema')

class VistaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vista
        fields = _f_base + ('nome', 'nome_modello')

class MansioneTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MansioneTranslation
        fields = '__all__'

class MansioneSerializer(serializers.ModelSerializer):
    translations = MansioneTranslationSerializer(many=True, read_only=True)
    class Meta:
        model = Mansione
        fields = _f_base + _f_itde 

class AttivitaTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttivitaTranslation
        fields = '__all__'

class AttivitaSerializer(serializers.ModelSerializer):
    translations = AttivitaTranslationSerializer(many=True, read_only=True)
    mansioni = serializers.PrimaryKeyRelatedField(many=True, queryset=Mansione.objects.all())
    class Meta:
        model = Attivita
        fields = _f_base + _f_itde + ('obbligo_foto', 'chiusura_auto_lavoro', 'tempo_stimato', 'tempo_aumento', 'mansioni')

class PrioritaTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrioritaTranslation
        fields = '__all__'

class PrioritaSerializer(serializers.ModelSerializer):
    translations = PrioritaTranslationSerializer(many=True, read_only=True)
    class Meta:
        model = Priorita
        fields = _f_base + _f_itde + ('valore', )

class AnnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anno
        fields = _f_base + ('anno', ) 

class SquadraTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SquadraTranslation
        fields = '__all__'

class SquadraSerializer(serializers.ModelSerializer):
    translations = SquadraTranslationSerializer(many=True, read_only=True)
    class Meta:
        model = Squadra
        fields = _f_base + _f_itde

class TipologiaTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipologiaTranslation
        fields = '__all__'

class TipologiaSerializer(serializers.ModelSerializer):
    translations = TipologiaTranslationSerializer(many=True, read_only=True)
    class Meta:
        model = Tipologia
        fields = _f_base + _f_itde + ('tipo', 'abbreviazione', 'ordine')

class CollaboratoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collaboratore
        fields = _f_base + ('dipendente', 'squadra', 'telefono', 'responsabile', 'mansioni', 'assenze', 'reperibilita', 'sigla', 'vista', )

class CdCTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CdCTranslation
        fields = '__all__'

class CdCSerializer(serializers.ModelSerializer):
    translations = CdCTranslationSerializer(many=True, read_only=True)
    class Meta:
        model = CdC
        fields = _f_base + _f_itde + ('annotazioni', )

class StrutturaTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = StrutturaTranslation
        fields = '__all__'

class StrutturaSerializer(serializers.ModelSerializer):
    translations = StrutturaTranslationSerializer(many=True, read_only=True)
    autorizzati = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = Struttura
        fields = _f_base + _f_itde + ('responsabile', 'cdc', 'telefono', 'autorizzati', )

class DirittoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diritto
        fields = _f_base + ('nome', 'capocantiere', 'caposquadra', 'coordinatore', 'operaio', 'struttura', 'ufficio', )

class EventoTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventoTranslation
        fields = '__all__'

class EventoSerializer(serializers.ModelSerializer):
    translations = EventoTranslationSerializer(many=True, read_only=True)
    class Meta:
        model = Evento
        fields = _f_base + _f_itde

class TagSerializer(EventoSerializer):
    class Meta(EventoSerializer.Meta):
        pass

class SegnalazioneSerializer(serializers.ModelSerializer):
    struttura = serializers.PrimaryKeyRelatedField(queryset=Struttura.objects.all())
    origine = serializers.PrimaryKeyRelatedField(many=False, queryset=Tipologia.objects.filter(tipo="SO"), required=False, allow_null=True)
    eventi = serializers.PrimaryKeyRelatedField(many=True, queryset=Evento.objects.all())
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all(), required=False, allow_null=True)
    tipo = serializers.PrimaryKeyRelatedField(queryset=Tipologia.objects.filter(tipo="ST"))
    stato = serializers.PrimaryKeyRelatedField(queryset=Tipologia.objects.filter(tipo="TO"))
    
    class Meta:
        model = Segnalazione
        fields = _f_base + _f_periodic + _f_description + _f_status + _f_d3 + ('data_pianificazione', 'struttura', 'origine', 'segnalatore', 'email', 'telefono', 'risposta', 'eventi', 'tags', 'tipo',  )
        
class SegnalazioneCompletaSerializer(serializers.ModelSerializer):
    struttura = StrutturaSerializer(many=False, read_only=True)
    origine = TipologiaSerializer(many=False, read_only=True, required=False, allow_null=True)
    eventi = EventoSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True, required=False, allow_null=True)
    tipo = TipologiaSerializer(many=False, read_only=True)
    stato = TipologiaSerializer(many=False, read_only=True)
    
    class Meta:
        model = Segnalazione
        fields = _f_base + _f_periodic + _f_description + _f_status + _f_d3 + ('data_pianificazione', 'struttura', 'origine', 'segnalatore', 'email', 'telefono', 'risposta', 'eventi', 'tags', 'tipo',  )

class InterventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Intervento
        fields = fields = _f_base  + _f_periodic + _f_description + _f_status + _f_rabs +  ('segnalazione', 'struttura', 'priorita', 'preposto', 'precedente', 'data_visibilita', 'data_urgente', 'data_esecuzione', 'provvisorio', )
        

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = _f_base + ('intervento', 'attivita', 'tempo_stimato',  'tempo_aumento', )

class FotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Foto
        fields = _f_gis + ('tipologia', 'intervento', 'collaboratore', 'foto', 'posizione', 'note', )

class LavoroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lavoro
        fields = _f_base + _f_description +_f_status + ('collaboratore', 'team', 'durata_prevista', 'caposquadra', 'accessorio', 'urgenza', 'mod_priorita', )

class TempiLavoroSerializer(serializers.ModelSerializer):
    class Meta:
        model = TempiLavoro
        fields = _f_base + ('lavoro', 'inizio', 'fine', 'note', )

class AllegatoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Allegato
        fields = _f_base + ('segnalazione', 'file', 'descrizione', )

class AnnotazioneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Annotazione
        fields = _f_base + ('lavoro', 'testo', )

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
