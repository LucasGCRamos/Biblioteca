from kivymd.app import MDApp #estende as funcionalidades do Kivy básico, fornecendo recursos e widgets adicionais com um design de Material Design.
from kivy.uix.boxlayout import BoxLayout #é um layout que organiza os widgets em uma direção (horizontal ou vertical)
from kivy.uix.scrollview import ScrollView #é um widget que permite rolar o conteúdo quando ele é maior do que a área visível
from kivy.uix.gridlayout import GridLayout #é um layout que organiza os widgets em uma grade bidimensional, dividindo o espaço disponível em linhas e colunas uniformes.
from kivy.uix.floatlayout import FloatLayout #é um layout que permite posicionar widgets em coordenadas específicas, oferecendo um controle mais preciso sobre a posição dos elementos na interface.
from kivymd.uix.button import MDRaisedButton #é um botão com estilo de Material Design que possui uma aparência elevada quando pressionado.
from kivymd.uix.label import MDLabel #usado para exibir texto na interface.
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField #é um campo de entrada de texto com estilo de Material Design, que fornece uma caixa de entrada interativa para os usuários inserirem texto.
from firebase_admin import credentials, db # é usada para autenticar o aplicativo no Firebase, enquanto db é usada para acessar o banco de dados em tempo real do Firebase.
import firebase_admin

#Esse trecho de código serve para inicializar a conexão entre o seu aplicativo Python e o projeto Firebase, permitindo que você use as funcionalidades e serviços oferecidos pelo Firebase.
cred = credentials.Certificate('ChavePv.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': '...'#aqui ficaria sua url do banco de dados, não compartilhado por questões de segurança
})

#Este é o método de inicialização (construtor) da classe. É chamado automaticamente quando se cria um novo objeto da classe Book. Ele aceita quatro parâmetros pedidos.
class Book:
    def __init__(self, key, title, author, read=False):
        self.key = key
        self.title = title
        self.author = author
        self.read = read


class BookApp(MDApp):
    def build(self): # Essa função é responsável por criar a interface de usuário (UI) do aplicativo.
        self.layout = FloatLayout() #  Cria um layout do tipo FloatLayout, que permite posicionar os widgets de forma livre em coordenadas X e Y.
        #Essas linhas criam campos de entrada de texto (MDTextField) e um botão de adicionar livro
        self.title_input = MDTextField(hint_text='Título do livro', font_size=16, multiline=False, pos_hint={'center_x': 0.5, 'top': 0.9})
        self.author_input = MDTextField(hint_text='Autor do livro', font_size=16, multiline=False, pos_hint={'center_x': 0.5, 'top': 0.8})
        self.add_button = MDRaisedButton(text='Adicionar Livro', on_release=self.add_book, size_hint=(0.3, None), height=40, pos_hint={'center_x': 0.5, 'top': 0.7})

        self.layout.add_widget(MDLabel(text='Lista de Livros', halign='center', font_style='H4', size_hint_y=None, height=40, pos_hint={'center_x': 0.5, 'top': 0.95}))
        self.layout.add_widget(self.title_input)
        self.layout.add_widget(self.author_input)
        self.layout.add_widget(self.add_button)

        self.buttons_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint=(0.5, None), height=40, pos_hint={'center_x': 0.5, 'top': 0.6})

        self.search_input = MDTextField(hint_text='Pesquisar por livro ou autor', font_size=16, multiline=False, size_hint=(0.7, None), height=40)
        self.search_button = MDRaisedButton(text='Pesquisar', on_release=self.search_books, size_hint=(0.3, None), height=40)

        self.buttons_layout.add_widget(self.search_input)
        self.buttons_layout.add_widget(self.search_button)

        self.layout.add_widget(self.buttons_layout) #uma parte superior da interface com os elementos "Lista de Livros", campos de entrada para título e autor, e o botão de adicionar livro. Abaixo disso, você terá o layout buttons_layout com o campo de entrada de pesquisa e o botão de pesquisa.

        #Adiciona o layout book_list ao ScrollView, para que o conteúdo da lista de livros seja exibido dentro do ScrollView.
        #Adiciona o ScrollView com a lista de livros à interface do aplicativo, dentro do layout principal self.layout.
        self.book_list_view = ScrollView(pos_hint={'center_x': 0.5, 'top': 0.5}, do_scroll_x=False, do_scroll_y=True)
        self.book_list_view.scroll_y = 1
        self.book_list = GridLayout(cols=1, spacing=10, size_hint_y=None, row_default_height=40, row_force_default=True)


        self.book_list_view.add_widget(self.book_list)
        self.layout.add_widget(self.book_list_view)

        self.update_list()

        return self.layout

    def add_book(self, instance):
        title = self.title_input.text.strip()
        #Essas linhas obtêm o texto inserido nos campos de entrada de título e autor (title_input e author_input) e removem quaisquer espaços em branco
        # extras no início ou no final usando o método strip(). Os valores dos campos de entrada são atribuídos às variáveis title e author.
        author = self.author_input.text.strip()
        if not title or not author:
            self.show_warning("Campos vazios", "Preencha tanto o título do livro quanto o nome do autor.")
            return
        if title and author:
            book_ref = db.reference('books')#Cria uma referência ao nó 'books' no banco de dados em tempo real do Firebase.
            new_book_ref = book_ref.push()# Isso cria um novo nó com uma chave única gerada automaticamente no banco de dados.
            new_book_ref.set({'title': title, 'author': author, 'read': False})#Define os valores do novo livro no nó criado anteriormente.
            self.title_input.text = ''  # Limpa o campo título do livro
            self.author_input.text = ''  # Limpa o campo autor do livro
            self.search_books(instance)  # Chama a função de pesquisa para atualizar a lista filtrada

    def update_list(self):
        self.book_list.clear_widgets()
        books_ref = db.reference('books')
        books = books_ref.get()
        if books:
            for key, book_data in books.items():
                book = Book(key=key, title=book_data['title'], author=book_data['author'], read=book_data['read'])
                if self.search_input.text.strip().lower() in book.title.lower() or self.search_input.text.strip().lower() in book.author.lower():
                    book_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=42)
                    title_label = MDLabel(text=book.title, font_size=18, size_hint_x=0.6, halign='center')
                    author_label = MDLabel(text=book.author, font_size=18, size_hint_x=0.3, halign='center')

                    # Criação de botões de ação (Lido/Não Lido e Excluir)
                    buttons_layout = GridLayout(cols=3, spacing=5, size_hint_x=0.6)
                    read_button = MDRaisedButton(text='Lido' if book.read else 'Não Lido', font_size=14, size_hint=(1, None), height=40)
                    read_button.bind(on_release=lambda x, book=book: self.toggle_read(book))# Associa a função toggle_read ao botão

                    delete_button = MDRaisedButton(text='Excluir', font_size=14, size_hint=(1, None), height=40)
                    delete_button.bind(on_release=lambda x, book=book: self.delete_book(book))# Associa a função delete_book ao botão

                    # Adiciona os botões ao layout de botões
                    buttons_layout.add_widget(read_button)
                    buttons_layout.add_widget(delete_button)

                    # Adiciona os rótulos de título e autor, juntamente com os botões, ao layout do livro
                    book_layout.add_widget(title_label)
                    book_layout.add_widget(author_label)
                    book_layout.add_widget(buttons_layout)

                    # Adiciona o layout do livro à lista de livros
                    self.book_list.add_widget(book_layout)

                    # Ajusta a altura da lista de livros com base no número de elementos filhos
                    self.book_list.height = len(self.book_list.children) * (200 + self.book_list.spacing[1])

                    # Rola a visualização da lista de livros para o topo
                    self.book_list_view.scroll_y = 1

    def show_warning(self, title, message):
        self.dialog = MDDialog(title=title, text=message, size_hint=(0.8, None))
        self.dialog.open()

    def toggle_read(self, book):
        book_ref = db.reference('books').child(book.key)
        book_ref.update({'read': not book.read})
        self.search_books(None)  # Chama a função de pesquisa para atualizar a lista filtrada

    def delete_book(self, book):
        book_ref = db.reference('books').child(book.key)
        book_ref.delete()
        self.search_books(None)  # Chama a função de pesquisa para atualizar a lista filtrada

    def search_books(self, instance):
        self.update_list()
        self.search_input.text = ''  # Limpa o campo de pesquisa após a busca


if __name__ == "__main__":
    BookApp().run()