import torch
from vislearnlabpy.models.multimodal_model import MultimodalModel
from vislearnlabpy.embeddings import utils
from vislearnlabpy.embeddings.generate_embeddings import EmbeddingConfig, EmbeddingGenerator
from multimodal.multimodal_lit import MultiModalLitModel


class CVCLGenerator(MultimodalModel):
    """Vision-language generator for CVCL (Vong et al.), the child-egocentric-video
    contrastive model. Same CLIP-shaped interface as vislearnlabpy's CLIPGenerator --
    encode_image takes a batched image tensor, encode_text takes tokenized text --
    except CVCL's tokenizer returns (tokens, lengths) instead of a single token
    tensor, so text_embeddings is overridden to batch-tokenize and pass both through.
    """

    def __init__(self, dataloader=None, device=None):
        model, preprocess = MultiModalLitModel.load_model()
        super().__init__(model, preprocess, dataloader, device)
        self.name = "cvcl"

    @property
    def embedding_dim(self) -> int:
        return int(self.model.model.args.get("embedding_dim", 128))

    def encode_image(self, image):
        return self.model.encode_image(image)

    def text_embeddings(self, words, normalize_embeddings=False):
        tokens, lengths = self.model.tokenize(words)
        tokens, lengths = tokens.to(self.device), lengths.to(self.device)
        with torch.no_grad():
            embeddings = self.model.encode_text(tokens, lengths)
        if normalize_embeddings:
            embeddings = utils.normalize_embeddings(embeddings)
        return embeddings


def cvcl_embedding_generator(device=None) -> EmbeddingGenerator:
    """Build an EmbeddingGenerator wrapping CVCLGenerator.

    Workaround: EmbeddingGenerator.generate_image_embeddings() always rebuilds
    self.model via _build_model(), which only knows the model_source values defined
    in vislearnlabpy (openai_clip/huggingface/huggingface_clip/silicon_menagerie) and
    has no "cvcl" case, so it would silently discard our model and fall back to
    CLIPGenerator. CVCL depends on the `multimodal` package, which is vendored
    locally in this repo rather than a real pip dependency of vislearnlabpy, so it
    can't be registered there as a normal MODEL_PRESETS entry. Patch _build_model on
    this instance so it keeps returning the CVCL model instead.
    """
    cvcl = CVCLGenerator(device=device)
    gen = EmbeddingGenerator(
        config=EmbeddingConfig(model_type="cvcl", output_type="doc", device=device),
        model=cvcl,
    )

    def _build_model(dataloader=None):
        cvcl.dataloader = dataloader
        return cvcl

    gen._build_model = _build_model
    return gen
