import numpy as np
import networkx as nx
from typing import Dict, List, Tuple, Optional, Any
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import json
import random
import requests
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import time
import base64
from io import BytesIO

class CardDifficulty(Enum):
    """카드 난이도"""
    EASY = 0
    GOOD = 1
    HARD = 2
    AGAIN = 3

@dataclass
class FlashCard:
    """플래시카드 클래스"""
    id: str
    front: str  # 질문/단서
    back: str   # 답/내용
    loci_id: str
    memory_palace_path: List[str]  # 기억의 궁전 경로
    
    # Spaced Repetition 관련
    easiness_factor: float = 2.5
    interval: int = 1  # 다음 복습까지 일수
    repetitions: int = 0
    next_review: datetime = field(default_factory=datetime.now)
    last_review: Optional[datetime] = None
    
    # 멀티미디어 요소
    image_url: Optional[str] = None
    audio_url: Optional[str] = None
    visual_cue: Optional[str] = None  # 시각적 단서 설명
    
    # 개인화 요소
    personal_associations: List[str] = field(default_factory=list)
    success_rate: float = 0.0
    total_attempts: int = 0
    correct_attempts: int = 0

@dataclass
class ChunkingProfile:
    """개인별 chunking 프로필"""
    user_id: str
    base_capacity: int = 7  # Miller's magic number
    current_capacity: int = 7
    max_tested_capacity: int = 7
    improvement_rate: float = 0.1
    test_history: List[Tuple[int, float]] = field(default_factory=list)  # (capacity, success_rate)
    
    def update_capacity(self, attempted_size: int, success_rate: float):
        """용량 테스트 결과를 바탕으로 프로필 업데이트"""
        self.test_history.append((attempted_size, success_rate))
        
        if success_rate >= 0.8:  # 80% 이상 성공
            if attempted_size > self.current_capacity:
                self.current_capacity = min(attempted_size, self.max_tested_capacity + 2)
                self.max_tested_capacity = max(self.max_tested_capacity, attempted_size)
        elif success_rate < 0.6:  # 60% 미만 성공
            self.current_capacity = max(3, self.current_capacity - 1)

class MultimediaProvider:
    """멀티미디어 리소스 제공자 (시뮬레이션)"""
    
    def __init__(self):
        # 실제로는 YouTube Data API, Unsplash API 등을 사용
        self.sample_images = {
            "apple": "https://example.com/apple.jpg",
            "book": "https://example.com/book.jpg",
            "physics": "https://example.com/physics.jpg",
            "math": "https://example.com/math.jpg",
        }
        
        self.sample_audio = {
            "nature": "https://example.com/nature.mp3",
            "classical": "https://example.com/classical.mp3",
            "ambient": "https://example.com/ambient.mp3",
        }
        
        # 실제 YouTube 무료 음원 예시들
        self.youtube_free_audio = [
            "YouTube Audio Library - Acoustic",
            "Creative Commons - Nature Sounds",
            "Royalty Free - Classical Piano",
        ]
    
    def get_relevant_image(self, content: str, keywords: List[str] = None) -> Optional[str]:
        """내용에 맞는 이미지 URL 반환"""
        content_lower = content.lower()
        
        # 키워드 매칭
        for keyword, url in self.sample_images.items():
            if keyword in content_lower:
                return url
        
        # 실제 구현시에는 Unsplash API 등 사용
        # return f"https://source.unsplash.com/400x300/?{'+'.join(keywords or ['study'])}"
        return "https://via.placeholder.com/400x300?text=Memory+Image"
    
    def get_background_audio(self, mood: str = "focus") -> Optional[str]:
        """분위기에 맞는 배경음 반환"""
        mood_mapping = {
            "focus": "ambient",
            "relaxed": "nature",
            "energetic": "classical"
        }
        
        audio_type = mood_mapping.get(mood, "ambient")
        return self.sample_audio.get(audio_type)
    
    def generate_visual_cue(self, content: str) -> str:
        """내용에 맞는 시각적 단서 생성"""
        cue_templates = [
            f"거대한 네온사인에 '{content[:10]}...'이 깜빡이고 있다",
            f"황금색 글씨로 '{content[:10]}...'이 벽에 새겨져 있다",
            f"홀로그램처럼 떠오르는 '{content[:10]}...' 이미지",
            f"마법의 책에서 빛나는 '{content[:10]}...' 글자들",
        ]
        return random.choice(cue_templates)

class SpacedRepetitionEngine:
    """간격 반복 학습 엔진 (SM-2 알고리즘 기반)"""
    
    def calculate_next_interval(self, card: FlashCard, difficulty: CardDifficulty) -> int:
        """다음 복습 간격 계산"""
        if difficulty == CardDifficulty.AGAIN:
            card.repetitions = 0
            card.interval = 1
        else:
            if card.repetitions == 0:
                card.interval = 1
            elif card.repetitions == 1:
                card.interval = 6
            else:
                card.interval = int(card.interval * card.easiness_factor)
            
            card.repetitions += 1
        
        # 난이도에 따른 easiness factor 조정
        if difficulty == CardDifficulty.EASY:
            card.easiness_factor += 0.1
        elif difficulty == CardDifficulty.HARD:
            card.easiness_factor -= 0.15
        elif difficulty == CardDifficulty.AGAIN:
            card.easiness_factor -= 0.2
        
        # easiness factor 범위 제한
        card.easiness_factor = max(1.3, card.easiness_factor)
        
        return card.interval
    
    def get_due_cards(self, cards: List[FlashCard]) -> List[FlashCard]:
        """복습 예정인 카드들 반환"""
        now = datetime.now()
        due_cards = [card for card in cards if card.next_review <= now]
        return sorted(due_cards, key=lambda x: x.next_review)
    
    def schedule_next_review(self, card: FlashCard, difficulty: CardDifficulty):
        """다음 복습 일정 예약"""
        interval = self.calculate_next_interval(card, difficulty)
        card.next_review = datetime.now() + timedelta(days=interval)
        card.last_review = datetime.now()

class ChunkingTester:
    """개인별 기억 용량 테스터"""
    
    def __init__(self):
        self.test_sequences = self._generate_test_sequences()
    
    def _generate_test_sequences(self) -> Dict[int, List[List[str]]]:
        """테스트용 시퀀스 생성"""
        sequences = {}
        
        # 숫자 시퀀스
        digit_sequences = {
            3: [['1', '4', '7'], ['2', '8', '5'], ['9', '3', '6']],
            5: [['1', '4', '7', '2', '9'], ['3', '8', '5', '1', '6'], ['7', '2', '9', '4', '3']],
            7: [['1', '4', '7', '2', '9', '5', '3'], ['8', '1', '6', '9', '2', '7', '4']],
            9: [['1', '4', '7', '2', '9', '5', '3', '8', '6'], ['7', '2', '9', '4', '1', '8', '5', '3', '6']],
        }
        
        # 단어 시퀀스
        word_sequences = {
            3: [['사과', '바나나', '포도'], ['고양이', '강아지', '토끼']],
            5: [['사과', '바나나', '포도', '딸기', '오렌지'], ['책', '연필', '지우개', '자', '가방']],
            7: [['월', '화', '수', '목', '금', '토', '일'], ['빨강', '주황', '노랑', '초록', '파랑', '남색', '보라']],
        }
        
        sequences.update(digit_sequences)
        sequences.update(word_sequences)
        
        return sequences
    
    def run_capacity_test(self, profile: ChunkingProfile, max_test_size: int = 12) -> int:
        """용량 테스트 실행"""
        print(f"\n=== 기억 용량 테스트 시작 ===")
        print(f"현재 예상 용량: {profile.current_capacity}")
        
        # 현재 용량보다 약간 높은 단계부터 테스트
        test_size = min(profile.current_capacity + 1, max_test_size)
        results = []
        
        for size in range(3, test_size + 1):
            if size in self.test_sequences:
                success_count = 0
                test_count = min(3, len(self.test_sequences[size]))
                
                for i in range(test_count):
                    sequence = self.test_sequences[size][i]
                    success = self._single_sequence_test(sequence, size)
                    if success:
                        success_count += 1
                
                success_rate = success_count / test_count
                results.append((size, success_rate))
                
                print(f"크기 {size}: {success_rate:.1%} 성공")
                
                # 성공률이 낮으면 테스트 중단
                if success_rate < 0.5:
                    break
        
        # 프로필 업데이트
        if results:
            best_size, best_rate = max(results, key=lambda x: x[1] if x[1] >= 0.6 else 0)
            profile.update_capacity(best_size, best_rate)
        
        print(f"테스트 완료! 새로운 권장 용량: {profile.current_capacity}")
        return profile.current_capacity
    
    def _single_sequence_test(self, sequence: List[str], size: int) -> bool:
        """단일 시퀀스 테스트 (시뮬레이션)"""
        print(f"\n다음 {size}개 항목을 순서대로 기억하세요:")
        print(" -> ".join(sequence))
        
        # 실제로는 사용자 입력을 받지만, 여기서는 시뮬레이션
        # 간단한 확률 모델: 크기가 클수록 어려움
        difficulty_factor = min(1.0, size / 10.0)
        success_probability = max(0.1, 1.0 - difficulty_factor * 0.8)
        
        time.sleep(1)  # 사용자가 기억하는 시간 시뮬레이션
        success = random.random() < success_probability
        
        print(f"결과: {'성공' if success else '실패'}")
        return success

class EnhancedMemoryPalace:
    """강화된 기억의 궁전 시스템"""
    
    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id
        self.cards: Dict[str, FlashCard] = {}
        self.loci_structure: Dict[str, Dict] = {}
        self.chunking_profile = ChunkingProfile(user_id)
        self.srs_engine = SpacedRepetitionEngine()
        self.chunking_tester = ChunkingTester()
        self.multimedia_provider = MultimediaProvider()
        
        # 학습 통계
        self.study_sessions: List[Dict] = []
        self.daily_stats: Dict[str, Dict] = defaultdict(lambda: {
            'cards_studied': 0,
            'correct_answers': 0,
            'study_time': 0
        })
    
    def create_loci_structure(self, structure: Dict[str, Dict]):
        """기억의 궁전 구조 설정"""
        self.loci_structure = structure
        print(f"기억의 궁전 구조가 설정되었습니다: {list(structure.keys())}")
    
    def add_flash_card(self, card_id: str, front: str, back: str, 
                      loci_id: str, keywords: List[str] = None,
                      personal_associations: List[str] = None) -> FlashCard:
        """플래시카드 생성 및 추가"""
        # 기억의 궁전 경로 생성
        memory_path = self._generate_memory_path(loci_id)
        
        # 멀티미디어 요소 추가
        image_url = self.multimedia_provider.get_relevant_image(back, keywords)
        audio_url = self.multimedia_provider.get_background_audio("focus")
        visual_cue = self.multimedia_provider.generate_visual_cue(back)
        
        card = FlashCard(
            id=card_id,
            front=front,
            back=back,
            loci_id=loci_id,
            memory_palace_path=memory_path,
            image_url=image_url,
            audio_url=audio_url,
            visual_cue=visual_cue,
            personal_associations=personal_associations or []
        )
        
        self.cards[card_id] = card
        print(f"카드 생성됨: {card_id}")
        print(f"  위치: {loci_id}")
        print(f"  경로: {' -> '.join(memory_path)}")
        print(f"  시각적 단서: {visual_cue}")
        
        return card
    
    def _generate_memory_path(self, target_loci: str) -> List[str]:
        """목표 위치까지의 기억 경로 생성"""
        if target_loci not in self.loci_structure:
            return [target_loci]
        
        # 간단한 경로 생성 (실제로는 더 복잡한 경로 알고리즘 사용)
        all_loci = list(self.loci_structure.keys())
        start_loci = all_loci[0] if all_loci else target_loci
        
        if start_loci == target_loci:
            return [target_loci]
        
        # BFS로 최단 경로 찾기 (간단한 버전)
        path = [start_loci, target_loci]
        return path
    
    def create_chunked_lesson(self, content_list: List[Tuple[str, str]], 
                             lesson_name: str) -> List[List[FlashCard]]:
        """개인 용량에 맞는 청크 단위로 레슨 생성"""
        chunk_size = self.chunking_profile.current_capacity
        chunks = []
        
        print(f"\n=== {lesson_name} 레슨 생성 ===")
        print(f"총 {len(content_list)}개 항목을 {chunk_size}개씩 나누어 학습")
        
        for i in range(0, len(content_list), chunk_size):
            chunk_content = content_list[i:i + chunk_size]
            chunk_cards = []
            
            for j, (front, back) in enumerate(chunk_content):
                # 각 청크별로 다른 loci 사용
                loci_id = f"loci_{(i // chunk_size) + 1}"
                card_id = f"{lesson_name}_chunk{(i // chunk_size) + 1}_item{j + 1}"
                
                card = self.add_flash_card(card_id, front, back, loci_id)
                chunk_cards.append(card)
            
            chunks.append(chunk_cards)
            print(f"청크 {len(chunks)}: {len(chunk_cards)}개 카드")
        
        return chunks
    
    def study_session(self, max_cards: int = 20) -> Dict[str, Any]:
        """학습 세션 실행"""
        session_start = datetime.now()
        due_cards = self.srs_engine.get_due_cards(list(self.cards.values()))
        
        if not due_cards:
            print("복습할 카드가 없습니다!")
            return {"status": "no_cards"}
        
        study_cards = due_cards[:max_cards]
        session_stats = {
            "cards_studied": 0,
            "correct_answers": 0,
            "start_time": session_start,
            "card_results": []
        }
        
        print(f"\n=== 학습 세션 시작 ===")
        print(f"복습할 카드 수: {len(study_cards)}")
        
        for card in study_cards:
            result = self._study_single_card(card)
            session_stats["card_results"].append(result)
            session_stats["cards_studied"] += 1
            
            if result["correct"]:
                session_stats["correct_answers"] += 1
        
        # 세션 완료 처리
        session_end = datetime.now()
        session_stats["end_time"] = session_end
        session_stats["study_time"] = (session_end - session_start).total_seconds()
        session_stats["accuracy"] = session_stats["correct_answers"] / session_stats["cards_studied"]
        
        self.study_sessions.append(session_stats)
        
        # 일일 통계 업데이트
        today = session_start.strftime("%Y-%m-%d")
        self.daily_stats[today]["cards_studied"] += session_stats["cards_studied"]
        self.daily_stats[today]["correct_answers"] += session_stats["correct_answers"]
        self.daily_stats[today]["study_time"] += session_stats["study_time"]
        
        self._print_session_summary(session_stats)
        return session_stats
    
    def _study_single_card(self, card: FlashCard) -> Dict[str, Any]:
        """단일 카드 학습"""
        print(f"\n--- 카드: {card.id} ---")
        print(f"위치: {card.loci_id}")
        print(f"경로: {' -> '.join(card.memory_palace_path)}")
        print(f"시각적 단서: {card.visual_cue}")
        
        if card.personal_associations:
            print(f"개인적 연상: {', '.join(card.personal_associations)}")
        
        print(f"\n질문: {card.front}")
        
        # 실제로는 사용자 입력을 받지만, 여기서는 시뮬레이션
        time.sleep(2)  # 사용자가 생각하는 시간
        
        print(f"정답: {card.back}")
        
        # 난이도 평가 시뮬레이션 (실제로는 사용자가 선택)
        difficulty_choices = list(CardDifficulty)
        # 카드의 성공률을 바탕으로 시뮬레이션
        if card.success_rate > 0.8:
            difficulty = random.choice([CardDifficulty.EASY, CardDifficulty.GOOD])
        elif card.success_rate > 0.6:
            difficulty = CardDifficulty.GOOD
        elif card.success_rate > 0.4:
            difficulty = CardDifficulty.HARD
        else:
            difficulty = random.choice([CardDifficulty.HARD, CardDifficulty.AGAIN])
        
        print(f"난이도 평가: {difficulty.name}")
        
        # 카드 통계 업데이트
        card.total_attempts += 1
        correct = difficulty in [CardDifficulty.EASY, CardDifficulty.GOOD]
        if correct:
            card.correct_attempts += 1
        card.success_rate = card.correct_attempts / card.total_attempts
        
        # 다음 복습 일정 설정
        self.srs_engine.schedule_next_review(card, difficulty)
        
        return {
            "card_id": card.id,
            "correct": correct,
            "difficulty": difficulty.name,
            "next_review": card.next_review.strftime("%Y-%m-%d")
        }
    
    def _print_session_summary(self, stats: Dict[str, Any]):
        """세션 요약 출력"""
        print(f"\n=== 세션 완료 ===")
        print(f"학습한 카드 수: {stats['cards_studied']}")
        print(f"정답률: {stats['accuracy']:.1%}")
        print(f"학습 시간: {stats['study_time']:.1f}초")
        
        # 다음 복습 예정 카드 수
        upcoming = len(self.srs_engine.get_due_cards(list(self.cards.values())))
        print(f"다음 복습 예정: {upcoming}개")
    
    def run_capacity_test(self):
        """기억 용량 테스트 실행"""
        return self.chunking_tester.run_capacity_test(self.chunking_profile)
    
    def get_study_analytics(self) -> Dict[str, Any]:
        """학습 분석 데이터 반환"""
        if not self.study_sessions:
            return {"message": "학습 데이터가 없습니다."}
        
        total_cards = sum(session["cards_studied"] for session in self.study_sessions)
        total_correct = sum(session["correct_answers"] for session in self.study_sessions)
        overall_accuracy = total_correct / total_cards if total_cards > 0 else 0
        
        return {
            "total_sessions": len(self.study_sessions),
            "total_cards_studied": total_cards,
            "overall_accuracy": overall_accuracy,
            "current_capacity": self.chunking_profile.current_capacity,
            "total_cards_in_system": len(self.cards),
            "daily_stats": dict(self.daily_stats)
        }
    
    def visualize_progress(self):
        """학습 진도 시각화"""
        if not self.study_sessions:
            print("시각화할 데이터가 없습니다.")
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # 1. 정확도 변화
        accuracies = [session["accuracy"] for session in self.study_sessions]
        ax1.plot(range(1, len(accuracies) + 1), accuracies, 'b-o')
        ax1.set_title('세션별 정확도 변화')
        ax1.set_xlabel('세션')
        ax1.set_ylabel('정확도')
        ax1.grid(True)
        
        # 2. 카드별 성공률
        card_success_rates = [(card.id[:10], card.success_rate) for card in self.cards.values() if card.total_attempts > 0]
        if card_success_rates:
            card_ids, success_rates = zip(*card_success_rates)
            ax2.bar(range(len(card_ids)), success_rates)
            ax2.set_title('카드별 성공률')
            ax2.set_xlabel('카드')
            ax2.set_ylabel('성공률')
            ax2.set_xticks(range(len(card_ids)))
            ax2.set_xticklabels(card_ids, rotation=45)
        
        # 3. 기억 용량 변화
        if self.chunking_profile.test_history:
            test_sizes, test_rates = zip(*self.chunking_profile.test_history)
            ax3.scatter(test_sizes, test_rates, c='red', alpha=0.7)
            ax3.set_title('기억 용량 테스트 결과')
            ax3.set_xlabel('테스트 크기')
            ax3.set_ylabel('성공률')
            ax3.grid(True)
        
        # 4. 일일 학습량
        daily_data = list(self.daily_stats.items())
        if daily_data:
            dates, stats = zip(*daily_data)
            daily_cards = [stat["cards_studied"] for stat in stats]
            ax4.bar(range(len(dates)), daily_cards)
            ax4.set_title('일일 학습 카드 수')
            ax4.set_xlabel('날짜')
            ax4.set_ylabel('카드 수')
            ax4.set_xticks(range(len(dates)))
            ax4.set_xticklabels([date[-5:] for date in dates], rotation=45)
        
        plt.tight_layout()
        plt.show()

def create_sample_lesson() -> List[Tuple[str, str]]:
    """샘플 레슨 데이터 생성"""
    return [
        ("What is the capital of France?", "Paris"),
        ("Newton's first law", "An object at rest stays at rest, an object in motion stays in motion"),
        ("Photosynthesis equation", "6CO2 + 6H2O + light energy → C6H12O6 + 6O2"),
        ("What is 15 × 17?", "255"),
        ("Who wrote '1984'?", "George Orwell"),
        ("Chemical symbol for gold", "Au"),
        ("Speed of light", "299,792,458 m/s"),
        ("Largest planet in our solar system", "Jupiter"),
        ("Year World War II ended", "1945"),
        ("Square root of 144", "12"),
        ("Author of 'Romeo and Juliet'", "William Shakespeare"),
        ("Boiling point of water at sea level", "100°C or 212°F"),
    ]

# 사용 예시 및 데모
if __name__ == "__main__":
    # 강화된 기억의 궁전 시스템 생성
    palace = EnhancedMemoryPalace("student_001")
    
    # 기억의 궁전 구조 설정
    loci_structure = {
        "loci_1": {"name": "현관", "description": "집의 입구"},
        "loci_2": {"name": "거실", "description": "편안한 휴식 공간"},
        "loci_3": {"name": "주방", "description": "요리하는 공간"},
        "loci_4": {"name": "서재", "description": "공부하는 공간"},
    }
    palace.create_loci_structure(loci_structure)
    
    # 1. 기억 용량 테스트
    print("=== 1단계: 개인 기억 용량 테스트 ===")
    optimal_capacity = palace.run_capacity_test()
    
    # 2. 청크 기반 레슨 생성
    print("\n=== 2단계: 적응형 레슨 생성 ===")
    lesson_content = create_sample_lesson()
    lesson_chunks = palace.create_chunked_lesson(lesson_content, "General_Knowledge")
    
    # 3. 학습 세션 실행
    print("\n=== 3단계: 학습 세션 시작 ===")
    
    # 여러 번의 학습 세션 시뮬레이션
    for session_num in range(3):
        print(f"\n--- 학습 세션 {session_num + 1} ---")
        session_result = palace.study_session(max_cards=8)
        
        if session_result.get("status") == "no_cards":
            # 새로운 카드들을 복습 대상으로 추가 (시간 조작)
            for card in list(palace.cards.values())[-5:]:
                card.next_review = datetime.now() - timedelta(minutes=1)
    
    # 4. 학습 분석 및 시각화
    print("\n=== 4단계: 학습 분석 ===")
    analytics = palace.get_study_analytics()
    
    print("\n학습 통계:")
    print(f"총 세션 수: {analytics['total_sessions']}")
    print(f"총 학습 카드 수: {analytics['total_cards_studied']}")
    print(f"전체 정확률: {analytics['overall_accuracy']:.1%}")
    print(f"현재 기억 용량: {analytics['current_capacity']}")
    print(f"시스템 내 총 카드 수: {analytics['total_cards_in_system']}")
    
    # 5. 진도 시각화
    print("\n=== 5단계: 진도 시각화 ===")
    palace.visualize_progress()
    
    # 6. 멀티미디어 플래시카드 예시
    print("\n=== 6단계: 멀티미디어 플래시카드 예시 ===")
    sample_card = list(palace.cards.values())[0]
    print(f"카드 ID: {sample_card.id}")
    print(f"이미지 URL: {sample_card.image_url}")
    print(f"음성 URL: {sample_card.audio_url}")
    print(f"시각적 단서: {sample_card.visual_cue}")
    
    print("\n=== 시스템 데모 완료 ===")
    print("실제 사용시에는:")
    print("1. YouTube Audio Library에서 무료 음원 연동")
    print("2. Unsplash/Pixabay API로 이미지 자동 검색")
    print("3. 사용자 입력 기반 실제 복습 진행")
    print("4. 웹/모바일 인터페이스로 편리한 사용")


# def main():
#     print("Hello from flashcard-app!")


# if __name__ == "__main__":
#     main()
