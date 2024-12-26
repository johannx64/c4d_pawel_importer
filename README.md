# C4D Pawel Importer

## Overview
The C4D Pawel Importer is a custom material importer designed for Cinema 4D (C4D). It facilitates batch importing of FBX files and sets up materials according to specific requirements, including conversions for People and Accessories.

## Features
- Batch imports FBX files.
- Converts materials for People and Accessories.
- Supports new model types, including Posed Plus with 3D Hair.

## New Model Types
Recently, we have introduced a new type of model called **Posed Plus**, which includes:
- **3D Hair**: This has a separate material that should connect the following maps:
  - Color
  - Specular
  - Roughness
  - Normal
  - Alpha

### Material Requirements
1. **Hair Material**:
   - Must connect the maps mentioned above.
   - Follows the same naming scheme as Accessories.

2. **Human Material**:
   - Now includes an Alpha map that should be assigned similarly to the Accessories.

3. **Ambient Occlusion Maps**:
   - Both Human and Hair materials now include Ambient Occlusion maps.
   - These should be mixed with Color maps using a multiply mode (0.3 value / 30%).

## Setup Instructions
All configurations should be set up as before, with the addition of:
- Utilizing Hair materials (similar to Accessories).
- Incorporating Ambient Occlusion Maps for both Hair and Human materials.

## Usage
To use the importer:
1. Ensure you have the required materials attached.
2. Run the importer script in Cinema 4D.
3. Follow the prompts to import your models.

## Contribution
If you would like to contribute to this project, please fork the repository and submit a pull request. Ensure that your code adheres to the existing style and includes appropriate tests.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact
For any inquiries or support, please contact Johann at johann9616@gmail.com.