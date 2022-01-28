from rest_framework import serializers

from core.models import Tag, Ingredient, Recipe


class TagSerializer(serializers.ModelSerializer):
    # serializador para los Tags

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id', )


class IngredientSerializer(serializers.ModelSerializer):
    # serializador para los ingredientes

    class Meta:
        model = Ingredient
        fields = ('id', 'name')
        read_only_fields = ('id', )


class RecipeSerializer(serializers.ModelSerializer):
    # serializador para las Recetas
    ingredients = serializers.PrimaryKeyRelatedField(many=True, queryset=Ingredient.objects.all())
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())

    class Meta:
        model = Recipe
        fields = ('id', 'title', 'ingredients', 'tags', 'time_minutes', 'price', 'link')
        read_only_fields = ('id', )

class RecipeDetailSerializer(RecipeSerializer):
    # serializa los detalles de una receta
    ingredients = IngredientSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    

class RecipeImageSerializer(serializers.ModelSerializer):
    # serializar imagenes

    class Meta:
        model = Recipe
        fields = ('id', 'image')
        read_only_fields = ('id',)