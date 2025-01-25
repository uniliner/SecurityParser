import fnmatch
import re

class v:
    def __init__(self, security_analyzer):
        self.security_analyzer = security_analyzer

    def _match_patterns(self, file_path, pattern_dict):
        """
        Match file path against a dictionary of patterns
        
        Args:
            file_path (str): Path of the file to check
            pattern_dict (dict): Dictionary of pattern groups
        
        Returns:
            list: Matched pattern groups with their risk scores
        """
        matched_patterns = []
        
        for group_name, group_data in pattern_dict.items():
            for pattern in group_data.get('patterns', []):
                # Convert GitHub pattern to fnmatch-compatible pattern
                modified_pattern = pattern.replace('**/', '**/').replace('{', '(').replace('}', ')')
                
                # Use regex to handle complex patterns
                regex_pattern = modified_pattern.replace('.', r'\.').replace('*', '.*')
                if re.search(regex_pattern, file_path):
                    matched_patterns.append({
                        'group': group_name,
                        'pattern': pattern,
                        'risk_score': group_data.get('risk_score', 0),
                        'rationale': group_data.get('rationale', '')
                    })
        
        return matched_patterns

    def filter_repository_contents(self, github_contents):
        """
        Filter GitHub repository contents based on security patterns
        
        Args:
            github_contents (list): List of file/directory information from GitHub API
        
        Returns:
            dict: Filtered contents with risk analysis
        """
        filtered_contents = {
            'critical_risk': [],
            'high_risk': [],
            'safe': []
        }
        
        for item in github_contents:
            file_path = item.get('path', '')
            
            # Check critical patterns
            critical_matches = self._match_patterns(file_path, self.security_analyzer.critical_patterns)
            if critical_matches:
                filtered_contents['critical_risk'].append({
                    'path': file_path,
                    'matches': critical_matches
                })
                continue
            
            # Check high-risk patterns
            high_risk_matches = self._match_patterns(file_path, self.security_analyzer.high_risk_patterns)
            if high_risk_matches:
                filtered_contents['high_risk'].append({
                    'path': file_path,
                    'matches': high_risk_matches
                })
                continue
            
            # Check contextual paths
            is_contextual = any(
                any(context in file_path for context in contexts)
                for contexts in [
                    self.security_analyzer.contextual_patterns['configuration_locations'],
                    self.security_analyzer.contextual_patterns['security_related_paths']
                ]
            )
            
            if is_contextual:
                filtered_contents['high_risk'].append({
                    'path': file_path,
                    'matches': [{'group': 'Contextual Path'}]
                })
            else:
                filtered_contents['safe'].append(file_path)
        
        return filtered_contents
    
