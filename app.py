from flask import Flask, render_template, request, send_file, redirect, url_for, flash
import requests
import os
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright
import urllib.parse

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # 適宜変更してください

def generate_brawl_stars_image(player_tag_input, language_input, club_name_input):
    # API キーとプレイヤータグの設定
    API_KEY = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6ImJiN2JmYWFkLWY1ZmYtNGFmNy1hNzdmLTcxN2QzZjQ0NjdjYyIsImlhdCI6MTczOTEwNjAwMiwic3ViIjoiZGV2ZWxvcGVyL2FlYTFmYjgzLTQxYmItOTk1Ni00N2M3LTEyOTY1MGQxMjM5NiIsInNjb3BlcyI6WyJicmF3bHN0YXJzIl0sImxpbWl0cyI6W3sidGllciI6ImRldmVsb3Blci9zaWx2ZXIiLCJ0eXBlIjoidGhyb3R0bGluZyJ9LHsiY2lkcnMiOlsiNDUuNzkuMjE4Ljc5Il0sInR5cGUiOiJjbGllbnQifV19.RE-DrAgWvlLG74XQXmq0Y6vEMU8FrECBiMR60K-MBq6ZADv6Lxhu9TyjQ9F36OoiVSAv79tMLF5CZTf5Ssce-A'
    original_player_tag = player_tag_input  # ユーザー入力
    encoded_player_tag = urllib.parse.quote(original_player_tag, safe='')
    headers = {
        'Authorization': f'Bearer {API_KEY}'
    }
    
    # 言語設定（0:英語, 1:日本語, 2:韓国語, 3:中国語, 4:フランス語, 5:スペイン語）
    language = language_input
    lang_dict = {
        0: {  # English
            "trophies": "Trophies",
            "current": "Current",
            "highest": "Highest",
            "ranked": "Ranked",
            "characters_owned": "Characters Owned",
            "avg_character_level": "Avg Character Level",
            "avg_trophies": "Avg Trophies",
            "gadgets_owned": "Gadgets Owned",
            "starpowers_owned": "Starpowers Owned",
            "victories": "Victories",
            "club_name": "Club Name",
            "id": "ID"
        },
        1: {  # Japanese
            "trophies": "トロフィー",
            "current": "現在",
            "highest": "最高",
            "ranked": "ランク",
            "characters_owned": "キャラ所有数",
            "avg_character_level": "平均キャラレベル",
            "avg_trophies": "平均トロフィー",
            "gadgets_owned": "ガジェット所有数",
            "starpowers_owned": "スターパワー所有数",
            "victories": "勝利数",
            "club_name": "クラブ名",
            "id": "ID"
        },
        2: {  # Korean
            "trophies": "트로피",
            "current": "현재",
            "highest": "최고",
            "ranked": "랭크",
            "characters_owned": "캐릭터 소유수",
            "avg_character_level": "평균 캐릭터 레벨",
            "avg_trophies": "평균 트로피",
            "gadgets_owned": "가젯 소유수",
            "starpowers_owned": "스타파워 소유수",
            "victories": "승리 수",
            "club_name": "클럽 이름",
            "id": "ID"
        },
        3: {  # Chinese
            "trophies": "奖杯",
            "current": "当前",
            "highest": "最高",
            "ranked": "排名",
            "characters_owned": "拥有角色",
            "avg_character_level": "平均角色等级",
            "avg_trophies": "平均奖杯",
            "gadgets_owned": "拥有小工具",
            "starpowers_owned": "拥有星能",
            "victories": "胜利数",
            "club_name": "俱乐部名称",
            "id": "ID"
        },
        4: {  # French
            "trophies": "Trophées",
            "current": "Actuel",
            "highest": "Le plus haut",
            "ranked": "Classé",
            "characters_owned": "Personnages possédés",
            "avg_character_level": "Niveau moyen des personnages",
            "avg_trophies": "Trophées moyens",
            "gadgets_owned": "Gadgets possédés",
            "starpowers_owned": "Pouvoirs étoilés possédés",
            "victories": "Victoires",
            "club_name": "Nom du club",
            "id": "ID"
        },
        5: {  # Spanish
            "trophies": "Trofeos",
            "current": "Actual",
            "highest": "Máximo",
            "ranked": "Clasificado",
            "characters_owned": "Personajes poseídos",
            "avg_character_level": "Nivel medio de personaje",
            "avg_trophies": "Trofeos promedio",
            "gadgets_owned": "Artilugios poseídos",
            "starpowers_owned": "Poderes estelares poseídos",
            "victories": "Victorias",
            "club_name": "Nombre del club",
            "id": "ID"
        }
    }
    lang = lang_dict.get(language, lang_dict[0])
    
    # プレイヤーデータ取得
    url = f'https://bsproxy.royaleapi.dev/v1/players/{encoded_player_tag}'
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception("Failed to retrieve data: " + str(response.json()))
    player_data = response.json()
    brawler_data = {b['name']: b for b in player_data.get('brawlers', [])}
    
    # Supercell ID（API から取得できなかった場合はデフォルト）
    supercell_id = player_data.get('supercellId', 'FranticHark')
    # ランク情報（なければトロフィー数を仮置き）
    ranked_max = '6866'
    ranked_current = '762'
    
    background_colors = {
        range(1, 4): "#C45B27",
        range(4, 10): "#7C81CA",
        range(10, 15): "#DD933C",
        range(15, 20): "#4BA5E6",
        range(20, 25): "#B43EEB",
        range(25, 30): "#53B771",
        range(30, 35): "#BF3243",
        range(35, 40): "#352773",
        range(40, 45): "#CAFDFE",
        range(45, 51): "#FFFFFF"  # tier 50 まで対応
    }
    
    def get_background_color(rank):
        for rank_range, color in background_colors.items():
            if rank in rank_range:
                return color
        return "#FFFFFF"
    
    all_characters = [
        "SHELLY", "COLT", "BULL", "BROCK", "RICO", "SPIKE", "BARLEY", "JESSIE", "NITA",
        "DYNAMIKE", "EL PRIMO", "MORTIS", "CROW", "POCO", "BO", "PIPER", "PAM", "TARA",
        "DARRYL", "PENNY", "FRANK", "GENE", "TICK", "LEON", "ROSA", "CARL", "BIBI", "8-BIT",
        "SANDY", "BEA", "EMZ", "MR. P", "MAX", "JACKY", "GALE", "NANI", "SPROUT", "SURGE",
        "COLETTE", "AMBER", "LOU", "BYRON", "EDGAR", "RUFFS", "STU", "BELLE", "SQUEAK", "GROM",
        "BUZZ", "GRIFF", "ASH", "MEG", "LOLA", "FANG", "EVE", "JANET", "BONNIE", "OTIS", "SAM",
        "GUS", "BUSTER", "CHESTER", "GRAY", "MANDY", "R-T", "WILLOW", "MAISIE", "HANK",
        "CORDELIUS", "DOUG", "PEARL", "CHUCK", "CHARLIE", "MICO", "KIT", "LARRY & LAWRIE",
        "MELODIE", "ANGELO", "DRACO", "LILY", "BERRY", "CLANCY", "MOE", "KENJI", "SHADE",
        "JUJU", "MEEPLE", "OLLIE"
    ]
    
    TIER_BASE_URL = "https://firebasestorage.googleapis.com/v0/b/idnect--com.firebasestorage.app/o/tier%2F"
    QUERY_STRING = "?alt=media&token="
    
    DATA = [
        {"id": 1, "token": "81967a3f-5fec-435e-a774-4acaf960f978"},
        {"id": 10, "token": "36a02ea4-9578-425e-aeb5-1fafb09ebcbe"},
        {"id": 11, "token": "f36eac28-7f72-4798-8309-359c91be9037"},
        {"id": 12, "token": "4da34144-3a39-4e4b-9b8f-6059211f7093"},
        {"id": 13, "token": "844bd938-18a4-41b4-9cd2-859bda63860f"},
        {"id": 14, "token": "0b6f663d-ebc4-44c3-96a0-25dfb8c56f8"},
        {"id": 15, "token": "b0b8d297-f0ef-48ba-81f5-abdaffb0d7da"},
        {"id": 16, "token": "e4f5d554-36e0-403d-aa4c-178255f3087a"},
        {"id": 17, "token": "e4900c95-3213-4e70-94b9-31cbebbb56aa"},
        {"id": 18, "token": "87ebdaef-5dbe-4d87-b6af-1153f2f17231"},
        {"id": 19, "token": "717ff56b-78fb-4de6-bed0-ca6149d622ca"},
        {"id": 2, "token": "004889c9-8ec2-454d-a283-afb5f32e44a1"},
        {"id": 20, "token": "34260c26-cf8e-49fa-b26e-4d9bc66ffe74"},
        {"id": 21, "token": "770b7ef1-7061-44e1-9517-fbd6dc012845"},
        {"id": 22, "token": "473050bf-ae6e-4734-8fa9-9e412f24f1dd"},
        {"id": 23, "token": "42201872-9e25-4a56-8d76-b9d67bf64098"},
        {"id": 24, "token": "8ddd9462-caf6-4899-aa33-c235b9aebeff"},
        {"id": 25, "token": "34c548f2-4fd8-4cff-9f62-4badde7f850b"},
        {"id": 26, "token": "4e09a222-9bf2-4afe-9b83-566ac83d5a0b"},
        {"id": 27, "token": "8ce9b408-be18-4df1-9308-61e306c2e9a3"},
        {"id": 28, "token": "2f9ad234-0b8c-4b2e-b6ae-96da7c760e2d"},
        {"id": 29, "token": "9d8f8646-2073-4d01-8ac7-2cd0e0670604"},
        {"id": 3, "token": "87a8b772-09df-4acc-af2f-9e8eb24a7f85"},
        {"id": 30, "token": "f2565b7a-9c64-45b0-8f3c-13fd3bb9def4"},
        {"id": 31, "token": "92e434dd-0e30-433b-9ba3-40b53f2cdb42"},
        {"id": 32, "token": "e50d8ce5-54fe-42c5-8091-a947889195ad"},
        {"id": 33, "token": "a411a12e-957a-45eb-bf8b-e630f561416d"},
        {"id": 34, "token": "7e6d22e8-e498-4fe3-bbf8-622c6b30ecc6"},
        {"id": 35, "token": "127f888b-08a0-4beb-9dba-c89cea09590f"},
        {"id": 36, "token": "3457ed94-f299-4533-af21-4e32759c5221"},
        {"id": 37, "token": "b381f2ee-c9a6-405a-ba11-652ad20a3c36"},
        {"id": 38, "token": "c52aed84-e99c-4339-a6ae-cae0c6f8bdb9"},
        {"id": 39, "token": "ceb2c990-8724-4419-b975-75ebe04c99cd"},
        {"id": 4, "token": "78c299e9-caa3-4173-a6ff-9a70297a6eca"},
        {"id": 40, "token": "6b58bd7a-7c0f-4faf-b054-04fc44c05100"},
        {"id": 41, "token": "41b485e4-3231-47df-9fe2-de17b226df1f"},
        {"id": 42, "token": "0555ce00-73b8-48b9-a387-92f2fed8a3d7"},
        {"id": 43, "token": "99b0b1b3-5714-4fda-be43-a86c498afb42"},
        {"id": 44, "token": "f65ec7d3-800c-43aa-becd-83fc3e0537fd"},
        {"id": 45, "token": "f402ca27-e5e8-4656-97b9-9520e22f3030"},
        {"id": 46, "token": "4828b0e4-c22d-4490-9d86-1df30263467a"},
        {"id": 47, "token": "fcd27640-d674-481b-a927-6a1cc20d5735"},
        {"id": 48, "token": "3568cfde-a492-4e9f-8484-07f0dc900683"},
        {"id": 49, "token": "e49ebd65-ce03-4a5f-a5af-e5846b18a7bb"},
        {"id": 5, "token": "22f98f4c-b461-4af2-a85e-5fe53ec98f1b"},
        {"id": 50, "token": "faca5bf9-93bd-4a7a-8e3b-175eb05382b9"},
        {"id": 51, "token": "0fb5446c-3a94-4eb2-a1b1-6e22a7009c17"},
        {"id": 6, "token": "78f81949-f330-484f-9714-97fe01dd4a02"},
        {"id": 7, "token": "6497b8c0-0b91-4719-a5f0-8582efe1ef0a"},
        {"id": 9, "token": "6bb16090-a948-44fa-8834-1cc899cb5a4b"},
    ]
    
    def generate_tier_url(tier_id, token):
        return f"{TIER_BASE_URL}{tier_id}.png{QUERY_STRING}{token}"
    
    # brawler 用のトークン辞書（キャラクター画像用）
    BRAWLER_BASE_URL = "https://firebasestorage.googleapis.com/v0/b/idnect--com.firebasestorage.app/o/brawler%2F"
    
    BRAWLER_TOKENS = {
        "8bit": "9b2337e3-2376-4354-904d-73f2553e2b1c",
        "amber": "07669b88-b47a-4660-8e6d-98c5b48af26a",
        "angelo": "f8606fa9-faa7-4b75-8e8f-d3ccdc3c2ea2",
        "ash": "0e9c5687-7a22-42a3-a720-7097725febbe",
        "barley": "9d495826-e7ad-4e45-8fc6-e56e7229c196",
        "bea": "fe5442c2-8cab-4887-aab7-b74bafabde83",
        "belle": "21ebc786-35c7-41fa-ae91-ce49db0a07f5",
        "berry": "d7d3652f-788e-4d3b-8707-296a81b3847a",
        "bibi": "4bac0891-64a3-4018-bbd9-ee914e18c316",
        "bo": "79d125ba-9537-4a49-8654-9c41fe47a69c",
        "bonnie": "7fa1678f-2e01-454b-b24b-1a149990069c",
        "brock": "b227b6c4-3ef1-4339-b235-2db440d2e6fa",
        "bull": "ad92ebbe-0420-44c1-be2e-7546919bf6b0",
        "buster": "5c525bd0-3f57-479e-8b89-57865f9549f2",
        "buzz": "562e2a6a-5246-441f-9052-f63f1c40cba7",
        "byron": "b61e51a6-10fe-4f3a-88e4-e145d62a0f44",
        "carl": "46a7adb8-60a4-43e6-8a7c-b173a20e820f",
        "charlie": "01c912ae-1a28-4da5-a305-de3bce2bbe19",
        "chester": "ebc36236-5087-4f43-9565-a874561b39c0",
        "chuck": "d712a1f1-574b-43f6-8ae5-f50c72732ddc",
        "clancy": "9da77f34-1313-480b-9272-849544d9fec8",
        "colette": "21bd4a8f-00de-49e4-bfac-7e7d29471837",
        "colt": "32e954fc-d6b4-4057-ba55-ede828971831",
        "cordelius": "96fa5cf8-412c-489f-ae69-c6795adc1a53",
        "crow": "a7892f9d-b109-4081-9427-99f8a3c3959d",
        "darryl": "985e6cd8-76f7-47a7-a9ab-a85db96d1e41",
        "doug": "13668b98-3ce7-432a-9970-a236916f4cea",
        "draco": "d9773664-ca6c-47b9-a506-a66d3b9ff73e",
        "dynamike": "0f33352a-e34e-4983-b43a-a7fe7f1aadb9",
        "edgar": "520ed17c-7469-4824-9ce1-26c00e6355de",
        "elprimo": "28e3f203-472b-441d-ac93-2b15ee68dc1a",
        "emz": "21b7dafc-f7c9-4933-8a05-d2225a9c8903",
        "eve": "f3eec9ca-6ce6-4605-aa46-e457efafc940",
        "fang": "40f5b65d-c469-4e13-97cb-4fafeeb30045",
        "frank": "78d30d69-8860-4949-a7c4-410becd8a04a",
        "gale": "408b2563-5403-4215-b729-3fc8830a8ebc",
        "gene": "c4d41549-4f4f-47d7-8eef-611bf4c3cc2b",
        "gray": "3637b901-0421-4c34-880e-efd5cf86edbc",
        "griff": "7a5c9a71-4452-41ec-874b-ca74acf106ee",
        "grom": "53276dd6-70e0-4b37-93c1-ee19e8b418c2",
        "gus": "d6b09ec2-7fd7-4590-a7db-da9568844cd8",
        "hank": "dc3b1bc2-96b9-4cb7-8c6b-8df1a5c3474a",
        "jacky": "de72bec7-5f1c-4610-a124-5f89b4d83a90",
        "janet": "0c97b332-9c8a-4cf4-93ba-76b4fe4911cf",
        "jessie": "423d04e5-7659-4d4e-bc5c-44d55c6188ab",
        "juju": "8d5e7d5e-0293-417b-987d-cb1fade95716",
        "kenji": "81b0faa6-c350-4375-9d3f-29d0762c9827",
        "kit": "dee62b38-a8f8-4b0d-ae76-80ebf2cc0601",
        "larry&lawrie": "84b79062-1dcf-4d57-80fa-ae4e5e962c50",
        "leon": "47ee04f4-885b-4986-b4ee-3a7c51810c0c",
        "lily": "b4e2bb61-1726-46fb-a07c-9e1c3b14c2b9",
        "lola": "8acdb56c-2abf-493d-908e-c20b34e695aa",
        "lou": "d736686a-caba-4450-ae52-03828eb1a239",
        "maisie": "a2e8a933-84d8-4490-bb9a-97d9b85f9aa9",
        "mandy": "dd3812af-bf58-44f7-b4a6-9d7c8b5d172e",
        "max": "01bbbc0d-bdde-4089-ba09-1374102e6ce3",
        "meeple": "b9e7a629-b8c4-4afa-8c4f-5bc9c344a5cc",
        "meg": "f778af12-e4f2-4df0-8694-bb4c75cebbf2",
        "melodie": "f054ba6e-a5a5-4b0a-9d57-efa606039d80",
        "mico": "8eaf58ed-fe1b-4abe-87af-aaada997ca0c",
        "moe": "e2fd72e9-42fa-4f67-8281-2437fa780cb5",
        "mortis": "ad0a3600-5eca-483c-b627-be38b7ee15f6",
        "mrp": "7bccf49f-ca95-4e64-968e-6283fb361ec6",
        "nani": "3b21adfc-a2f6-43e6-a7ac-41bcbffe0f3a",
        "nita": "aaa38688-ab4b-4a91-b3c1-f90877ae8a8d",
        "ollie": "9bfe76f1-53d2-44b0-9419-cbd782653f63",
        "otis": "449e4ee6-eebb-4897-b6e1-7cf6ac925159",
        "pam": "9d2586fa-0391-42fe-a91b-64dd75fce41c",
        "pearl": "af874d4c-7365-4b11-949e-eac97cf9f68d",
        "penny": "c9ab7727-a9f7-41f3-8216-7f7f73f28f7f",
        "piper": "b1b8fcff-45a3-482a-ad0c-7f85d911bc01",
        "poco": "be188db2-782f-413a-b668-e7eac6e5b128",
        "rico": "2cbafa4e-c4b0-46ab-bbc5-bdf7a29ada93",
        "rosa": "cdd78268-b268-476a-90a1-597527d1551b",
        "rt": "520c5f56-0d37-42c4-991f-8c42b8ced6f8",
        "ruffs": "d08e9e3f-bd32-4d72-b0c1-8b9a969ffffa",
        "sam": "1490f602-fb69-45e1-97a5-f9e1f4a98e9f",
        "sandy": "8dd86261-9160-4f9e-88bf-31fb4639ecd0",
        "shade": "63b8081f-6b90-4bc5-bcf1-92d0b5d1921a",
        "shelly": "e3295f42-38b1-42a4-a0f5-f5d7de98c967",
        "spike": "295769fc-5895-4d38-964c-16ba4666a3ab",
        "sprout": "eecc916c-100e-45c8-9e5b-87a0a8155ccf",
        "squeak": "1f357fdd-e47a-4397-8f31-209beb2b965b",
        "stu": "3b911663-3060-4e42-a855-4417f9ad1c02",
        "surge": "7d9cb544-ffde-46fb-9f35-9388821bf314",
        "tara": "8da73dac-a20f-4327-b7e3-6064c8301e01",
        "tick": "56400ba5-cb80-4e2f-a67a-a62a985892c6",
        "willow": "1e672597-91af-4425-9870-ea8e913b43da"
    }
    
    def get_brawler_url(brawler_name: str) -> str:
        """brawler のポートレート画像のフル URL を返す"""
        formatted_name = brawler_name.lower().replace(" ", "").replace("&", "_").replace(".", "").replace("-", "")
        if brawler_name.strip().lower() == "larry & lawrie":
            formatted_name = "larry_and_lawrie"
        name_mapping = {
            "elprimo": "elprimo",
            "mrp": "mrp",
            "8bit": "8bit",
            "rt": "rt",
            "larry_and_lawrie": "larry&lawrie"
        }
        if formatted_name in name_mapping:
            formatted_name = name_mapping[formatted_name]
    
        if formatted_name not in BRAWLER_TOKENS:
            print(f"Warning: Unknown brawler: {brawler_name} (formatted as {formatted_name})")
            return None
    
        return f"{BRAWLER_BASE_URL}{formatted_name}_portrait.png?alt=media&token={BRAWLER_TOKENS[formatted_name]}"
    
    def get_rank_image(trophies):
        try:
            trophies_val = int(trophies)
        except:
            return ""
        if trophies_val < 1500:
            return "https://firebasestorage.googleapis.com/v0/b/idnect--com.firebasestorage.app/o/ranked%2Ficon_ranked_bronze.png?alt=media&token=be3d287d-3b6e-4c00-9478-6eae09b0d19b"
        elif trophies_val < 3000:
            return "https://firebasestorage.googleapis.com/v0/b/idnect--com.firebasestorage.app/o/ranked%2Ficon_ranked_silver.png?alt=media&token=6759bf30-6e1c-4600-a89e-c2018cc72399"
        elif trophies_val < 4500:
            return "https://firebasestorage.googleapis.com/v0/b/idnect--com.firebasestorage.app/o/ranked%2Ficon_ranked_gold.png?alt=media&token=16f336fe-79a0-462a-8126-2e2e2d7d7f2f"
        elif trophies_val < 6000:
            return "https://firebasestorage.googleapis.com/v0/b/idnect--com.firebasestorage.app/o/ranked%2Ficon_ranked_diamond.png?alt=media&token=e6a5bd1e-3fbd-401a-bf9c-c76b08502ed5"
        elif trophies_val < 7500:
            return "https://firebasestorage.googleapis.com/v0/b/idnect--com.firebasestorage.app/o/ranked%2Ficon_ranked_mythic.png?alt=media&token=73bc82b3-ad69-4094-a63e-36916ec88803"
        elif trophies_val < 9000:
            return "https://firebasestorage.googleapis.com/v0/b/idnect--com.firebasestorage.app/o/ranked%2Ficon_ranked_legendary.png?alt=media&token=9a2bd5c4-2935-43aa-aef4-00c4ab0a1f8c"
        else:
            return "https://firebasestorage.googleapis.com/v0/b/idnect--com.firebasestorage.app/o/ranked%2Ficon_ranked_masters.png?alt=media&token=4425e66c-b198-439d-98a0-3d7cb681edde"
    
    brawlers_final = []
    for character in all_characters:
        brawler = brawler_data.get(character, None)
        if not brawler:
            for key, value in brawler_data.items():
                if key.lower() == character.lower():
                    brawler = value
                    break
        if brawler:
            owned = True
            rank = brawler['rank']
            trophies = brawler['trophies']
            max_trophies = brawler['highestTrophies']
            power = brawler['power']
            if rank == 4:
                color = get_background_color(3)
            else:
                color = get_background_color(rank)
            is_light_background = rank >= 40
            max_trophies_color = '#808080' if is_light_background else 'white'
            tier_data = next((item for item in DATA if item["id"] == rank), None)
            if tier_data:
                tier_image = f"{TIER_BASE_URL}{tier_data['id']}.png{QUERY_STRING}{tier_data['token']}"
            else:
                tier_image = f"{TIER_BASE_URL}default.png?alt=media&token=default"
            gadgets_owned = len(brawler.get('gadgets', []))
            starpowers_owned = len(brawler.get('starPowers', []))
        else:
            owned = False
            rank = 0
            trophies = 0
            max_trophies = 0
            power = 0
            color = "#808080"
            tier_image = ""
            max_trophies_color = "white"
            gadgets_owned = 0
            starpowers_owned = 0
    
        image_url = get_brawler_url(character)
        if image_url is None:
            image_url = f"{BRAWLER_BASE_URL}default_portrait.png?alt=media&token=default"
    
        brawlers_final.append({
            'name': character,
            'rank': rank,
            'trophies': trophies,
            'max_trophies': max_trophies,
            'power': power,
            'color': color,
            'image': image_url,
            'tierImage': tier_image,
            'max_trophies_color': max_trophies_color,
            'owned': owned,
            'gadgets': gadgets_owned,
            'starpowers': starpowers_owned,
        })
    
     brawlers_final.sort(key=lambda x: x['trophies'], reverse=True)
    
    owned_count = sum(1 for b in brawlers_final if b['owned'])
    total_count = len(all_characters)
    average_level = round(sum(b['power'] for b in brawlers_final if b['owned']) / owned_count, 1) if owned_count > 0 else 0
    average_trophies = round(sum(b['trophies'] for b in brawlers_final if b['owned']) / owned_count, 1) if owned_count > 0 else 0
    owned_gadgets_total = sum(b['gadgets'] for b in brawlers_final if b['owned'])
    owned_starpowers_total = sum(b['starpowers'] for b in brawlers_final if b['owned'])
    
    brawler_html_blocks = []
    for b in brawlers_final:
        level_html = f'''
            <div class="absolute bottom-0 left-0 w-[50px] h-[50px] bg-pink-500 flex items-center justify-center text-white text-2xl font-bold rounded-full">
                {b['power']}
            </div>
        ''' if b['owned'] else ''
    
        if not b['owned']:
            additional_html = f'''
            <img src="https://firebasestorage.googleapis.com/v0/b/idnect--com.firebasestorage.app/o/locked_360.png?alt=media&token=953a8aee-3bb6-462d-abe2-d95c35088bd3" alt="Locked" style="max-width:77px; max-height:77px;" class="absolute right-0 top-1/2 transform -translate-y-1/2 object-contain">
            '''
        else:
            additional_html = f'''
            <img src="{b['tierImage']}" alt="Tier" style="max-width:77px; max-height:77px;" class="absolute top-0 right-0 object-contain">
            <div class="absolute bottom-6 right-4 text-center text-black text-2xl font-bold bg-white p-1 rounded-md flex items-center" style="width: 90px; height: 40px;">
                <img src="https://firebasestorage.googleapis.com/v0/b/idnect--com.firebasestorage.app/o/icon_trophy.png?alt=media&token=55b55940-179c-4ebd-9e5e-7dcd64f0e1cc" class="w-8 h-8 mr-2">
                <p>{b['trophies']}</p>
            </div>
            <div class="absolute bottom-0 right-4 text-center text-1.7xl font-bold" style="color: {b['max_trophies_color']};">
                Max: {b['max_trophies']}
            </div>
            '''
        brawler_html_blocks.append(f"""
        <div class="w-[273px] h-[154px] relative flex items-center justify-start" style="background-color: {b['color']};">
            <img src="{b['image']}" alt="{b['name']}" style="max-width:197px; max-height:154px;" class="object-contain">
            {level_html}
            {additional_html}
        </div>
        """)
    
    brawler_html_final = '\n'.join(brawler_html_blocks)
    
    ranked_current_image = get_rank_image(ranked_current)
    ranked_max_image = get_rank_image(ranked_max)
    
    html_stats_sections = f"""
    <div class="flex flex-row justify-between space-x-4">
        <div class="flex flex-col items-center bg-gray-100 p-4 rounded-lg">
            <p class="font-bold text-2xl">
                <img src="https://firebasestorage.googleapis.com/v0/b/idnect--com.firebasestorage.app/o/icon_trophy.png?alt=media&token=55b55940-179c-4ebd-9e5e-7dcd64f0e1cc" class="inline-block w-8 h-8 mr-2">{lang['trophies']}
            </p>
            <p class="text-xl">{lang['current']}: {player_data.get('trophies')}</p>
            <p class="text-xl">{lang['highest']}: {player_data.get('highestTrophies')}</p>
        </div>
        <div class="flex flex-col items-center bg-gray-100 p-4 rounded-lg">
            <p class="font-bold text-2xl">
                <img src="https://firebasestorage.googleapis.com/v0/b/idnect--com.firebasestorage.app/o/ranked%2Ficon_ranked_front.png?alt=media&token=f57dbbac-cfb7-457d-8b33-2c66f8c14169" alt="Ranked Front" class="inline-block mr-2" style="max-width:2em; max-height:2em; object-fit: contain;">{lang['ranked']}
            </p>
            <div class="flex items-center">
                <img src="{ranked_current_image}" alt="Current Ranked" class="inline-block mr-2" style="max-width:2em; max-height:2em; object-fit: contain;">
                <p class="text-xl">{lang['current']}: {ranked_current}</p>
            </div>
            <div class="flex items-center">
                <img src="{ranked_max_image}" alt="Highest Ranked" class="inline-block mr-2" style="max-width:2em; max-height:2em; object-fit: contain;">
                <p class="text-xl">{lang['highest']}: {ranked_max}</p>
            </div>
        </div>
        <div class="flex flex-col items-center bg-gray-100 p-4 rounded-lg">
            <p class="font-bold text-2xl">
                <img src="https://firebasestorage.googleapis.com/v0/b/idnect--com.firebasestorage.app/o/unlocked_360.png?alt=media&token=4952ed95-7ee0-4c3f-a138-c6bd27f4aed7" class="inline-block w-8 h-8 mr-2">{lang['characters_owned']}
            </p>
            <p class="text-xl">{owned_count} / {total_count}</p>
            <p class="font-bold text-2xl mt-2">
                <img src="https://firebasestorage.googleapis.com/v0/b/idnect--com.firebasestorage.app/o/powerpoint_360.png?alt=media&token=a656e31d-e68c-4bbb-a1c2-57a2ff253ad4" class="inline-block w-8 h-8 mr-2">{lang['avg_character_level']}
            </p>
            <p class="text-xl">{average_level}</p>
            <p class="font-bold text-2xl mt-2">
                <img src="https://firebasestorage.googleapis.com/v0/b/idnect--com.firebasestorage.app/o/icon_trophy.png?alt=media&token=55b55940-179c-4ebd-9e5e-7dcd64f0e1cc" class="inline-block w-8 h-8 mr-2">{lang['avg_trophies']}
            </p>
            <p class="text-xl">{average_trophies}</p>
        </div>
        <div class="flex flex-col items-center bg-gray-100 p-4 rounded-lg">
            <p class="font-bold text-2xl">
                <img src="https://firebasestorage.googleapis.com/v0/b/idnect--com.firebasestorage.app/o/gadget.png?alt=media&token=0d886b65-90ca-429b-81ce-04ef5d353fb6" class="inline-block w-8 h-8 mr-2">{lang['gadgets_owned']}
            </p>
            <p class="text-xl">{owned_gadgets_total} / {total_count*2}</p>
            <p class="font-bold text-2xl mt-2">
                <img src="https://firebasestorage.googleapis.com/v0/b/idnect--com.firebasestorage.app/o/starpower.png?alt=media&token=b4b6f829-5b9b-4b0b-8127-403e1fda56c0" class="inline-block w-8 h-8 mr-2">{lang['starpowers_owned']}
            </p>
            <p class="text-xl">{owned_starpowers_total} / {total_count*2}</p>
        </div>
        <div class="flex flex-col items-center bg-gray-100 p-4 rounded-lg">
            <p class="font-bold text-4xl text-center">{lang['victories']}</p>
            <div class="flex items-center justify-center mt-2">
                <img src="https://firebasestorage.googleapis.com/v0/b/idnect--com.firebasestorage.app/o/3v3.jpg?alt=media&token=76a4b594-f39a-4632-b2c1-3e7b55570d86" alt="3v3" class="w-8 h-8 mr-2">
                <p class="text-4xl text-center">{player_data.get('3vs3Victories')}</p>
            </div>
            <div class="flex items-center justify-center mt-2">
                <img src="https://firebasestorage.googleapis.com/v0/b/idnect--com.firebasestorage.app/o/showdown_icon.png?alt=media&token=e419cdb4-c089-427f-8137-2829f27ce2bc" alt="Solo" class="w-8 h-8 mr-2">
                <p class="text-4xl text-center">{player_data.get('soloVictories')}</p>
            </div>
            <div class="flex items-center justify-center mt-2">
                <img src="https://firebasestorage.googleapis.com/v0/b/idnect--com.firebasestorage.app/o/trio_showdown_icon.png?alt=media&token=9ebb22d4-b364-4e4b-8311-ed21009e869f" alt="Duo" class="w-8 h-8 mr-2">
                <p class="text-4xl text-center">{player_data.get('duoVictories')}</p>
            </div>
        </div>
    </div>
    """
    
    created_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html_content_final = f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP&display=swap" rel="stylesheet">
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body {{ margin: 0; padding: 0; font-family: 'Noto Sans JP', sans-serif; }}
        </style>
    </head>
    <body>
        <div class="w-[2850px] h-[1800px] bg-white text-black p-8">
            <div class="flex justify-between items-start mb-4">
                <div class="flex flex-col space-y-4">
                    <div class="flex items-center p-4">
                        <img src="https://firebasestorage.googleapis.com/v0/b/idnect--com.firebasestorage.app/o/icon%20main%20cornered.png?alt=media&token=df91d390-8ad8-44a5-b4a2-f4d96239727c" alt="Icon Pin" class="mr-4" style="width: 3em; height: 3em;">
                        <div class="flex items-center">
                            <h1 class="font-bold" style="font-size: 3em;">{player_data.get('name')}</h1>
                            <div class="ml-8 flex items-center" style="font-size: 2em;">
                                <img src="https://firebasestorage.googleapis.com/v0/b/idnect--com.firebasestorage.app/o/id_logo_360.png?alt=media&token=9378d7b0-f1f6-48ef-988f-f316e5701bb8" alt="Supercell ID" class="inline-block mr-2" style="max-width:2em; max-height:2em; object-fit: contain;">
                                {supercell_id}
                            </div>
                        </div>
                    </div>
                    <div class="flex items-center p-4" style="font-size: 2em;">
                        <p>{lang['id']}: {original_player_tag}</p>
                    </div>
                    <div class="flex items-center p-4" style="font-size: 2em;">
                        <img src="https://firebasestorage.googleapis.com/v0/b/idnect--com.firebasestorage.app/o/club_360.png?alt=media&token=e6fa0765-8399-4a9a-a111-8fab6b10ad7e" alt="Club Icon" class="mr-2" style="width: 2em; height: 2em;">
                        <p>{lang['club_name']}: {club_name_input}</p>
                    </div>
                </div>
                <div>
                    {html_stats_sections}
                </div>
            </div>
            <div class="grid grid-cols-10 gap-0 mt-8" id="characters">
                {brawler_html_final}
            </div>
            <div class="flex justify-between items-end mt-8">
                <div class="text-xl">
                    {created_datetime}
                </div>
                <div class="flex items-center">
                    <p class="text-xl mr-2">http://IDNect.com</p>
                    <img src="https://firebasestorage.googleapis.com/v0/b/idnect--com.firebasestorage.app/o/IDnest.jpg?alt=media&token=292de0fe-cf2b-4039-9e65-64d4523868c3" alt="IDNect Logo" class="w-16 h-16">
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    with open('brawl_stars.html', 'w', encoding='utf-8') as f:
        f.write(html_content_final)
    
    async def render_html():
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(viewport={'width': 2850, 'height': 1800})
            file_path = os.path.abspath('brawl_stars.html')
            await page.goto(f'file://{file_path}')
            await page.wait_for_timeout(5000)
            await page.screenshot(path='brawl_stars.png', full_page=True)
            await browser.close()
    
    asyncio.run(render_html())

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        player_tag = request.form.get('player_tag')
        language = int(request.form.get('language', 1))
        club_name = request.form.get('club_name', 'パムおば教')
        try:
            generate_brawl_stars_image(player_tag, language, club_name)
        except Exception as e:
            flash(str(e))
            return redirect(url_for('index'))
        return send_file('brawl_stars.png', as_attachment=True)
    return render_template('index.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Renderが指定するPORTを取得（デフォルト10000）
    app.run(host="0.0.0.0", port=port, debug=True)
