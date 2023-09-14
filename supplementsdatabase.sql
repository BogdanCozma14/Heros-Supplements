PGDMP     (                    {           supplements    15.4    15.4     �           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            �           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            �           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            �           1262    16398    supplements    DATABASE     �   CREATE DATABASE supplements WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'English_United Kingdom.1250';
    DROP DATABASE supplements;
                postgres    false            �           0    0    DATABASE supplements    COMMENT     �   COMMENT ON DATABASE supplements IS 'This database is used for the cs50 final project - A website designed for a company that sells supplements and gym accessories.';
                   postgres    false    3325            �            1259    16400    products    TABLE     �   CREATE TABLE public.products (
    id integer NOT NULL,
    url_image text,
    description text,
    price numeric(10,2),
    category text
);
    DROP TABLE public.products;
       public         heap    postgres    false            �            1259    16399    products_id_seq    SEQUENCE     �   CREATE SEQUENCE public.products_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 &   DROP SEQUENCE public.products_id_seq;
       public          postgres    false    215            �           0    0    products_id_seq    SEQUENCE OWNED BY     C   ALTER SEQUENCE public.products_id_seq OWNED BY public.products.id;
          public          postgres    false    214            e           2604    16403    products id    DEFAULT     j   ALTER TABLE ONLY public.products ALTER COLUMN id SET DEFAULT nextval('public.products_id_seq'::regclass);
 :   ALTER TABLE public.products ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    214    215    215            �          0    16400    products 
   TABLE DATA           O   COPY public.products (id, url_image, description, price, category) FROM stdin;
    public          postgres    false    215   �                   0    0    products_id_seq    SEQUENCE SET     =   SELECT pg_catalog.setval('public.products_id_seq', 5, true);
          public          postgres    false    214            g           2606    16407    products products_pkey 
   CONSTRAINT     T   ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (id);
 @   ALTER TABLE ONLY public.products DROP CONSTRAINT products_pkey;
       public            postgres    false    215            �   �   x�}�=� Eg�o1����M���..(�6m(i��/�_������sr3��N�ꑾ���_�d��5%:���9���\}'a���	N��������-";F��Fт©o�t�� 4�.'���<t���_�XAbO菆/��.��6�e`j&�q�"��*�{�ό�ʊ����M�m{     