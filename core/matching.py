import os
import json

class MatchMaker:
    def __init__(self, similarity_data, quality_weight=0.5):
        self.similarity_data = similarity_data
        self.quality_weight = quality_weight
        self.all_participants = self._get_unique_participants()
        self.match_scores = self._calculate_match_scores()
        
    def _get_unique_participants(self):
        participants = set()
        for entry in self.similarity_data:
            participants.add(entry[0])
            for match in entry[1:]:
                if match != "No matches found":
                    participants.add(match)
        return participants
    
    def _calculate_match_scores(self):
        scores = {}
        for entry in self.similarity_data:
            email = entry[0]
            for i, match in enumerate(entry[1:]):
                if match != "No matches found":
                    score = 1.0 - (i / len(entry[1:]))
                    scores[(email, match)] = score
                    scores[(match, email)] = score
        return scores
    
    def create_pairs(self):
        pairs = []
        unpaired = set(self.all_participants)
        used_emails = set()
        
        # Sort by number of potential matches
        participants = []
        for entry in self.similarity_data:
            participant_email = entry[0]
            matches = [m for m in entry[1:] if m != "No matches found"]
            participants.append((participant_email, matches))
            
        participants.sort(
            key=lambda x: len(x[1]),
            reverse=self.quality_weight < 0.5
        )
        
        # First pass matching
        pairs, unpaired, used_emails = self._first_pass_matching(
            participants, pairs, unpaired, used_emails)
            
        # Second pass for remaining singles
        if unpaired and self.quality_weight < 0.8:
            pairs, unpaired = self._second_pass_matching(
                pairs, unpaired, self.similarity_data)
        
        # Validate final pairs
        validated_pairs, final_unpaired = self._validate_pairs(pairs, unpaired)
        
        return validated_pairs, final_unpaired
    
    def _first_pass_matching(self, participants, pairs, unpaired, used_emails):
        """First pass matching with quality-weighted pairing"""
        for participant, potential_matches in participants:
            if participant in used_emails:
                continue

            best_match = None
            best_score = -1

            for match in potential_matches:
                if match in used_emails:
                    continue
                    
                score = self.match_scores.get((participant, match), 0)
                # Adjust score based on quality weight
                adjusted_score = score * self.quality_weight + (1 - self.quality_weight) * (1 / (len(potential_matches) or 1))
                
                if adjusted_score > best_score:
                    best_score = adjusted_score
                    best_match = match

            if best_match:
                pairs.append([participant, best_match])
                used_emails.add(participant)
                used_emails.add(best_match)
                unpaired.discard(participant)
                unpaired.discard(best_match)
                
        return pairs, unpaired, used_emails
        
    def _second_pass_matching(self, pairs, unpaired, similarity_data):
        """Second pass to match remaining singles"""
        retry_unpaired = list(unpaired)
        remaining_unpaired = set(unpaired)
        
        while len(retry_unpaired) >= 2:
            current = retry_unpaired[0]
            best_match = None
            best_score = -1
            
            for match in retry_unpaired[1:]:
                score = self.match_scores.get((current, match), 0)
                if score > best_score:
                    best_score = score
                    best_match = match
                    
            if best_match:
                pairs.append([current, best_match])
                retry_unpaired.remove(current)
                retry_unpaired.remove(best_match)
                remaining_unpaired.discard(current)
                remaining_unpaired.discard(best_match)
            else:
                retry_unpaired.remove(current)
                
        return pairs, remaining_unpaired
        
    def _validate_pairs(self, pairs, unpaired):
        """Validate pairs and ensure no duplicates"""
        validated_pairs = []
        paired_emails = set()
        final_unpaired = set(unpaired)
        
        for pair in pairs:
            if pair[0] not in paired_emails and pair[1] not in paired_emails:
                validated_pairs.append(pair)
                paired_emails.add(pair[0])
                paired_emails.add(pair[1])
            else:
                if pair[0] not in paired_emails:
                    final_unpaired.add(pair[0])
                if pair[1] not in paired_emails:
                    final_unpaired.add(pair[1])
                    
        return validated_pairs, sorted(list(final_unpaired))
