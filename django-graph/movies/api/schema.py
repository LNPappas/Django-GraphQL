import graphene
from graphene import relay
from graphene_django.types import DjangoObjectType
from .models import Movie, Director
import graphql_jwt
from graphql_jwt.decorators import login_required
from graphene_django.filter import DjangoFilterConnectionField

class MovieType(DjangoObjectType):
    class Meta:
        model = Movie
        
    movie_age = graphene.String()
    
    def resolve_movie_age(self, info):
        return "Old Movie" if self.year < 2000 else "New Movie"
    
class DirectorType(DjangoObjectType):
    class Meta:
        model = Director
    
# relay implementation
class MovieNode(DjangoObjectType):
    class Meta:
        model=Movie
        filter_fields = ['title', 'year']
        interfaces = (relay.Node, )    
        


class Query(graphene.ObjectType):
    # all_movies = graphene.List(MovieType)
    all_movies = DjangoFilterConnectionField(MovieNode)
    
    movie = graphene.Field(MovieType, id=graphene.Int(), title=graphene.String())
    all_directors = graphene.List(DirectorType)
    
    def resolve_all_directors(self, info, **kwargs):
        return Director.objects.all()
    
    # @login_required
    # def resolve_all_movies(self, info, **kwargs):
    #     return Movie.objects.all()
    
    def resolve_movie(self, info, **kwargs):
        id = kwargs.get('id')
        title = kwargs.get('title')
        
        if id:
            return Movie.objects.get(pk=id)
        
        if title:
            return Movie.objects.get(title=title)
        return "Doesn't Exist"

class MovieCreateMutation(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        year = graphene.Int(required=True)
        
    movie = graphene.Field(MovieType)
    
    def mutate(self, info, title, year):
        movie = Movie.objects.create(title=title, year=year)
        return MovieCreateMutation(movie=movie)
    
class MovieUpdateMutation(graphene.Mutation):
    class Arguments:
        title = graphene.String()
        year = graphene.Int()
        id = graphene.ID(required=True)
    
    movie = graphene.Field(MovieType)
    
    def mutate(self, info, id, title, year):
        try:
            movie = Movie.objects.get(pk=id)
            if title:
                movie.title = title
            if year:
                movie.year = year
            movie.save()
            return MovieUpdateMutation(movie=movie)
        except:
            raise Exception("Movie not in database")
        
class MovieDeleteMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
    
    movie = graphene.Field(MovieType)
    
    def mutate(self, info, id):
        try:
            movie = Movie.objects.get(pk=id)
            movie.delete()
            return MovieUpdateMutation(movie=None)
        except:
            raise Exception("Movie not in database, Cannot delete movie that does not exist")
        
            
        
    
# Base Class
class Mutation:
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    
    create_movie = MovieCreateMutation.Field()
    update_movie = MovieUpdateMutation.Field()
    delete_movie = MovieDeleteMutation.Field()